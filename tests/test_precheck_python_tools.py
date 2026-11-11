"""Direct regression for precheck helpers that had no dedicated coverage."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import pytest

from lifecycle_fixtures import valid_payload

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / 'review-k1-function/scripts'
CACHE_BASE = PROJECT_ROOT / '.cache/fast-precheck'
SHA = 'a' * 40


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, encoding='utf-8')


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    return path


@pytest.fixture
def cache_root():
    path = CACHE_BASE / ('pytest-' + uuid.uuid4().hex)
    try:
        yield path
    finally:
        assert path.resolve().is_relative_to(CACHE_BASE.resolve())
        shutil.rmtree(path, ignore_errors=True)


def cache_key(project_tmp, **parts):
    source = write(project_tmp / ('key-' + uuid.uuid4().hex + '.json'),
                   {'contract': 'alignment-v1-unlimited', 'documentVersion': 'rev553', **parts})
    result = run('fast-precheck-cache.py', 'key', '--input', source)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_cache_round_trip_is_keyed_immutable_and_expires(project_tmp, cache_root):
    key = cache_key(project_tmp, target=SHA)
    assert key != cache_key(project_tmp, target='b' * 40)
    assert key == cache_key(project_tmp, target=SHA)
    common = ['--root', cache_root, '--kind', 'diff-index', '--key', key]
    miss = run('fast-precheck-cache.py', 'get', *common, '--output', project_tmp / 'miss.json')
    assert miss.returncode == 2 and json.loads(miss.stdout)['code'] == 'CACHE_MISS'
    assert not (project_tmp / 'miss.json').exists()

    payload = write(project_tmp / 'payload.json', {'paths': ['src/reward.go']})
    stored = run('fast-precheck-cache.py', 'put', *common, '--input', payload, '--now', '2026-11-01T00:00:00Z')
    assert stored.returncode == 0 and json.loads(stored.stdout)['code'] == 'CACHE_STORED'
    write(payload, {'paths': ['other']})
    again = run('fast-precheck-cache.py', 'put', *common, '--input', payload, '--now', '2026-11-01T00:00:00Z')
    assert json.loads(again.stdout)['code'] == 'CACHE_EXISTS'

    hit = run('fast-precheck-cache.py', 'get', *common, '--output', project_tmp / 'hit.json', '--now', '2026-11-01T23:59:59Z')
    assert hit.returncode == 0 and json.loads(hit.stdout)['code'] == 'CACHE_HIT'
    assert json.loads((project_tmp / 'hit.json').read_text(encoding='utf-8')) == {'paths': ['src/reward.go']}
    expired = run('fast-precheck-cache.py', 'get', *common, '--output', project_tmp / 'late.json', '--now', '2026-11-02T00:00:00Z')
    assert expired.returncode == 2 and json.loads(expired.stdout)['reason'] == 'expired'
    assert not (project_tmp / 'late.json').exists()


def test_cache_rejects_tampered_entries_secrets_and_outside_paths(project_tmp, cache_root, tmp_path):
    key = cache_key(project_tmp, target=SHA)
    common = ['--root', cache_root, '--kind', 'requirements', '--key', key]
    secret = write(project_tmp / 'secret.json', {'rows': [{'Access-Token': 'x'}]})
    refused = run('fast-precheck-cache.py', 'put', *common, '--input', secret)
    assert refused.returncode == 4 and 'SENSITIVE_CACHE_FIELD' in refused.stderr
    assert not list(cache_root.rglob('*.json'))

    payload = write(project_tmp / 'payload.json', {'requirements': ['REQ-1']})
    assert run('fast-precheck-cache.py', 'put', *common, '--input', payload).returncode == 0
    entry = next(cache_root.rglob('*.json'))
    value = json.loads(entry.read_text(encoding='utf-8'))
    value['payload'] = {'requirements': ['REQ-2']}
    write(entry, value)
    tampered = run('fast-precheck-cache.py', 'get', *common, '--output', project_tmp / 'out.json')
    assert tampered.returncode == 3 and not (project_tmp / 'out.json').exists()

    outside = write(tmp_path / 'payload.json', {'requirements': []})
    assert 'OUTSIDE_FUNCTIONPREVIEW' in run('fast-precheck-cache.py', 'put', *common, '--input', outside).stderr
    assert 'CACHE_ROOT_OUTSIDE' in run('fast-precheck-cache.py', 'put', '--root', project_tmp, '--kind', 'requirements',
                                       '--key', key, '--input', payload).stderr
    assert 'INVALID_CACHE_KIND' in run('fast-precheck-cache.py', 'put', '--root', cache_root, '--kind', 'reports',
                                       '--key', key, '--input', payload).stderr


def config_request(project_tmp, rows):
    source = write(project_tmp / ('config-' + uuid.uuid4().hex + '.json'), rows)
    return {'id': 'CFG-1', 'inputPath': str(source), 'sourcePath': 'json/reward.json', 'targetSha': SHA,
            'workbook': 'reward.xlsx', 'table': 'reward', 'affectedRequirementIds': ['REQ-1'],
            'requiredFields': ['id', 'min', 'max', 'weight'], 'primaryKey': 'id',
            'range': {'minField': 'min', 'maxField': 'max', 'expectedStart': 1, 'expectedEnd': 20},
            'weight': {'field': 'weight', 'expectedTotal': 100}}


HEADER = {'id': 'id', 'min': 'min', 'max': 'max', 'weight': 'weight'}
ROWS = [HEADER, {'id': 1, 'min': 1, 'max': 10, 'weight': 60}, {'id': 2, 'min': 11, 'max': 20, 'weight': 40}]


def validate_config(project_tmp, request):
    output = project_tmp / ('result-' + uuid.uuid4().hex + '.json')
    result = run('validate-config-json.py', '--request', write(project_tmp / 'request.json', request), '--output', output)
    return result, (json.loads(output.read_text(encoding='utf-8')) if output.exists() else None)


def test_generated_config_json_passes_only_as_secondary_evidence(project_tmp):
    result, report = validate_config(project_tmp, config_request(project_tmp, ROWS))
    assert result.returncode == 0, result.stderr
    assert report['status'] == '通过' and report['authority'] == '次级证据' and report['dataRowCount'] == 2
    assert '不能替代正式 XLSX' in report['limitation']


@pytest.mark.parametrize('mutate,failed_check', [
    (lambda rows: rows[2].update(id=1), 'primary-key'),
    (lambda rows: rows[2].update(min=12), 'range-continuity'),
    (lambda rows: rows[2].update(max=19), 'range-boundary'),
    (lambda rows: rows[2].update(weight=30), 'weight-total'),
    (lambda rows: rows[2].update(weight=0), 'weight-values'),
])
def test_generated_config_json_reports_each_data_defect(project_tmp, mutate, failed_check):
    rows = deepcopy(ROWS)
    mutate(rows)
    result, report = validate_config(project_tmp, config_request(project_tmp, rows))
    assert result.returncode == 0 and report['status'] == '发现异常'
    assert failed_check in [c['id'] for c in report['checks'] if c['status'] != '通过']


def test_generated_config_json_refuses_inputs_outside_tmp_and_movable_refs(project_tmp, tmp_path):
    request = config_request(project_tmp, ROWS)
    outside = write(tmp_path / 'rows.json', ROWS)
    result, report = validate_config(project_tmp, {**request, 'inputPath': str(outside)})
    assert result.returncode == 4 and 'INPUT_OUTSIDE_TMP' in result.stderr and report is None
    result, report = validate_config(project_tmp, {**request, 'targetSha': 'dev_NK-1'})
    assert result.returncode == 4 and 'INVALID_TARGET_SHA' in result.stderr and report is None


def alignment_input(project_tmp, mutate=None):
    payload = deepcopy(valid_payload())
    if mutate:
        mutate(payload)
    return write(project_tmp / ('handoff-' + uuid.uuid4().hex + '.json'),
                 {k: payload[k] for k in ('alignment', 'metadata', 'requirements') if k in payload})


def test_alignment_handoff_cli_accepts_completed_record(project_tmp):
    result = run('requirement_alignment.py', '--input', alignment_input(project_tmp))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['code'] == 'ALIGNMENT_COMPLETED'


@pytest.mark.parametrize('mutate,error', [
    (lambda p: p.pop('alignment'), 'ALIGNMENT_REQUIRED'),
    (lambda p: p['alignment'].update(status='in_progress'), 'ALIGNMENT_NOT_COMPLETED'),
    (lambda p: p['metadata'].update(documentVersion='rev-next'), 'ALIGNMENT_'),
    (lambda p: p['alignment'].update(repositories=[{**r, 'target': 'f' * 40} for r in p['metadata']['repositories']]),
     'ALIGNMENT_SNAPSHOT_MISMATCH'),
])
def test_alignment_handoff_cli_blocks_unconfirmed_or_drifted_records(project_tmp, mutate, error):
    result = run('requirement_alignment.py', '--input', alignment_input(project_tmp, mutate))
    assert result.returncode == 4 and error in result.stderr
