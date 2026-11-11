from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'review-k1-function/scripts/runtime_acceptance.py'


@pytest.fixture
def runtime(monkeypatch):
    assert SCRIPT.exists(), 'runtime acceptance executor is missing'
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location('runtime_acceptance', SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def sample(tmp_path):
    baseline = {'metadata': {'documentVersion': 'rev553', 'testcaseDocumentVersion': 'rev553'},
                'testcases': [{'id': 'TC-1', 'requirementIds': ['REQ-1'], 'expected': '迁移并重登一致'}]}
    source = tmp_path / 'baseline.json'
    source.write_text(json.dumps(baseline), encoding='utf-8')
    (tmp_path / 'evidence.json').write_text('{"observation":"actual server state"}', encoding='utf-8')
    plan = {'schemaVersion': 1, 'runId': 'test-run', 'baselineFile': 'baseline.json',
            'baselineSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'assertions': [
                {'id': 'TC-1/migrate', 'testcaseId': 'TC-1', 'expected': '正常迁移成功',
                 'action': '执行正常迁移', 'phase': 0, 'dependsOn': [], 'requiredEvidence': ['protocol', 'server']},
                {'id': 'TC-1/relogin', 'testcaseId': 'TC-1', 'expected': '重登后状态一致',
                 'action': '重登目标服', 'phase': 1, 'dependsOn': ['TC-1/migrate'], 'requiredEvidence': ['runtime']}]}
    return plan, tmp_path


def evidence(*kinds):
    return [{'kind': k, 'path': 'evidence.json'} for k in kinds]


def passed(state, aid, *kinds):
    state['results'][aid] = {'status': 'passed', 'observation': '权威状态已核对', 'evidence': evidence(*kinds)}


def finish(state):
    state['environmentEvidence'] = evidence('runtime')
    state['cleanup'] = {'verified': True, 'evidence': evidence('runtime'), 'retainedChanges': '迁移结果保留'}


def test_partial_result_must_return_action_and_prevent_final_publish(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'partial', 'observation': '只有请求成功',
                                     'evidence': evidence('protocol'), 'nextAction': '查询权威状态'}
    result = runtime.evaluate(plan, state, root)
    assert result['nextActions'][0]['action'] == '查询权威状态'
    assert result['canFinalize'] is False
    with pytest.raises(runtime.RuntimeContractError, match='RUNNABLE_OR_UNFINISHED'):
        runtime.publish(plan, state, root, root / 'report')
    assert not (root / 'report').exists()


def test_failed_main_assertion_does_not_hide_pending_independent_assertion(runtime, sample):
    plan, root = sample
    plan['assertions'][1]['dependsOn'] = []
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'failed', 'observation': '未落地', 'evidence': evidence('server')}
    result = runtime.evaluate(plan, state, root)
    assert result['caseResults']['TC-1'] == '失败'
    assert result['canFinalize'] is False
    assert result['nextActions'][0]['id'] == 'TC-1/relogin'


def test_environment_blocker_with_available_jenkins_path_remains_actionable(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'blocked', 'blocker': {
        'kind': 'environment', 'reason': '缺独立活动', 'attempts': [{'action': '检查活动 GM', 'outcome': '仅全服范围'}],
        'nextAction': '部署已授权独立服', 'options': {'gm': 'unavailable', 'jenkins': 'available'}}}
    result = runtime.evaluate(plan, state, root)
    assert result['canFinalize'] is False
    assert result['nextActions'][0]['action'] == '部署已授权独立服'


def test_assertions_cannot_disappear_or_change_after_execution_begins(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    plan['assertions'].pop()
    with pytest.raises(runtime.RuntimeContractError, match='PLAN_CHANGED'):
        runtime.evaluate(plan, state, root)


def test_initial_plan_cannot_drop_baseline_testcase(runtime, sample):
    plan, root = sample
    plan['assertions'][0]['testcaseId'] = 'OTHER'
    with pytest.raises(runtime.RuntimeContractError, match='CASE_COVERAGE'):
        runtime.initialize(plan, root)


def test_isolated_or_gm_evidence_cannot_pass_runtime_assertion(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'gm', 'isolated')
    with pytest.raises(runtime.RuntimeContractError, match='EVIDENCE_SCOPE'):
        runtime.evaluate(plan, state, root)


def test_static_failure_does_not_close_an_unexecuted_runtime_assertion(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'failed', 'observation': '只有源码推断', 'evidence': evidence('static')}
    with pytest.raises(runtime.RuntimeContractError, match='EVIDENCE_SCOPE'):
        runtime.evaluate(plan, state, root)


def test_forward_time_gate_rejects_unfinished_expiring_case_and_backwards(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    with pytest.raises(runtime.RuntimeContractError, match='PHASE_INCOMPLETE'):
        runtime.check_advance(plan, state, root, 1)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    runtime.check_advance(plan, state, root, 1)
    state['currentPhase'] = 1
    with pytest.raises(runtime.RuntimeContractError, match='TIME_MUST_ADVANCE'):
        runtime.check_advance(plan, state, root, 0)


def test_vague_blocker_or_unconfirmed_exclusion_is_rejected(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    for result in [{'status': 'blocked', 'blocker': {'reason': '缺环境'}}, {'status': 'excluded', 'reason': '以后再验'}]:
        state['results']['TC-1/migrate'] = result
        with pytest.raises(runtime.RuntimeContractError):
            runtime.evaluate(plan, state, root)


def test_full_pass_requires_environment_and_cleanup_and_writes_escaped_report(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    assert runtime.evaluate(plan, state, root)['canFinalize'] is False
    finish(state)
    state['results']['TC-1/relogin']['observation'] = '<script>bad()</script>'
    result = runtime.publish(plan, state, root, root / 'report')
    assert result['fullyAccepted'] is True
    html = (root / 'report/summary.html').read_text(encoding='utf-8')
    assert '<script>bad()' not in html
    assert '&lt;script&gt;' in html
    assert (root / 'report/runtime-result.json').exists()


def test_real_blocker_can_close_round_but_never_fully_accept(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    state['results']['TC-1/relogin'] = {'status': 'blocked', 'blocker': {
        'kind': 'environment', 'reason': '测试节点资源无法申请',
        'attempts': [{'action': '查询 Jenkins', 'outcome': '目标节点离线'}],
        'options': {'gm': 'unavailable', 'jenkins': 'exhausted'}, 'nextAction': '节点恢复后部署并重登'}}
    finish(state)
    result = runtime.evaluate(plan, state, root)
    assert result['canFinalize'] is True
    assert result['fullyAccepted'] is False
    assert result['caseResults']['TC-1'] == '部分验证'


def test_dependency_recovery_requeues_previously_blocked_assertion(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'failed', 'observation': '迁移失败', 'evidence': evidence('server')}
    state['results']['TC-1/relogin'] = {'status': 'blocked', 'blocker': {
        'kind': 'dependency', 'assertionId': 'TC-1/migrate', 'reason': '没有落地角色',
        'attempts': [{'action': '查询目标角色', 'outcome': '迁移尚未成功'}],
        'nextAction': '重登目标服核对持久化', 'options': {}}}
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    result = runtime.evaluate(plan, state, root)
    assert result['nextActions'][0]['id'] == 'TC-1/relogin'
    assert result['canFinalize'] is False


def test_missing_evidence_or_changed_baseline_cannot_be_published(runtime, sample):
    plan, root = sample
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    (root / 'evidence.json').unlink()
    with pytest.raises(runtime.RuntimeContractError, match='EVIDENCE_FILE_MISSING'):
        runtime.evaluate(plan, state, root)
    (root / 'baseline.json').write_text('{}', encoding='utf-8')
    with pytest.raises(runtime.RuntimeContractError, match='BASELINE_CHANGED'):
        runtime.evaluate(plan, state, root)


def test_cli_rejects_premature_publish_without_creating_output(sample):
    import subprocess
    import sys
    plan, root = sample
    (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    args = ['--plan', str(root / 'plan.json'), '--state', str(root / 'state.json')]
    initialized = subprocess.run([sys.executable, str(SCRIPT), 'init', *args], capture_output=True, encoding='utf-8')
    assert initialized.returncode == 0, initialized.stdout + initialized.stderr
    result = subprocess.run([sys.executable, str(SCRIPT), 'publish', *args, '--output', str(root / 'final')], capture_output=True, encoding='utf-8')
    assert result.returncode == 1
    assert json.loads(result.stdout)['error'] == 'RUNNABLE_OR_UNFINISHED'
    assert not (root / 'final').exists()


@pytest.mark.parametrize('mutation,error', [
    (lambda p,s: (p['assertions'][1].update(phase=0), p['assertions'][0].update(dependsOn=['TC-1/relogin'])), 'DEPENDENCY_CYCLE'),
    (lambda p,s: s['results'].pop('TC-1/relogin'), 'ASSERTION_COVERAGE'),
])
def test_dependency_cycles_and_missing_result_rows_are_rejected(runtime, sample, mutation, error):
    plan, root = sample
    state = runtime.initialize(plan, root)
    mutation(plan, state)
    if error == 'DEPENDENCY_CYCLE':
        with pytest.raises(runtime.RuntimeContractError, match=error): runtime.initialize(plan, root)
    else:
        with pytest.raises(runtime.RuntimeContractError, match=error): runtime.evaluate(plan, state, root)


@pytest.fixture
def scheduled(sample):
    plan, root = sample
    plan.update(schemaVersion=2, acceptanceMode='development',
                documentBaseline={'status': 'precheck_confirmed', 'source': 'design-doc',
                                  'confirmedVersion': 'rev553', 'currentVersion': 'rev553',
                                  'confirmedAt': '2026-10-21T09:00:00+08:00',
                                  'checkedAt': '2026-10-21T10:00:00+08:00',
                                  'precheckRunId': 'precheck-1', 'evidence': evidence('static')},
                executionGroups=[
                    {'id': 'enter', 'batch': 0, 'owner': 'tester-a', 'setup': '准备可迁移账号',
                     'assertionIds': ['TC-1/migrate'],
                     'resources': [{'id': 'unity-a', 'access': 'write'}]},
                    {'id': 'relogin', 'batch': 0, 'owner': 'tester-a', 'setup': '核对已迁移状态',
                     'assertionIds': ['TC-1/relogin'],
                     'resources': [{'id': 'unity-a', 'access': 'write'}]}])
    return plan, root


def test_regression_report_labels_scope_by_case_type(runtime, scheduled):
    plan, root = scheduled
    plan['acceptanceMode'] = 'mainline_regression'
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    result = runtime.publish(plan, state, root, root / 'report')
    assert result['acceptanceMode'] == 'mainline_regression'
    assert result['fullyAccepted'] is True
    report = (root / 'report/summary.html').read_text(encoding='utf-8')
    assert '版本日验收' in report and '按原单类型确定范围' in report
    assert '当前文档已是预检确认后的版本' in report


def test_changed_document_cannot_claim_precheck_freshness(runtime, scheduled):
    plan, root = scheduled
    plan['documentBaseline']['currentVersion'] = 'rev554'
    with pytest.raises(runtime.RuntimeContractError, match='DOCUMENT_BASELINE_MISMATCH'):
        runtime.initialize(plan, root)


def test_unreadable_document_can_record_work_but_cannot_fully_accept(runtime, scheduled):
    plan, root = scheduled
    plan['documentBaseline'].update(status='needs_review', currentVersion='', reason='当前源文档不可读')
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    result = runtime.evaluate(plan, state, root)
    assert result['canFinalize'] is True
    assert result['fullyAccepted'] is False
    assert result['documentStatus'] == '待复核'
    runtime.publish(plan, state, root, root / 'report')
    assert '当前源文档不可读' in (root / 'report/summary.html').read_text(encoding='utf-8')


def test_schedule_preserves_group_order_and_individual_results(runtime, scheduled):
    plan, root = scheduled
    plan['assertions'][1]['phase'] = 0
    plan['executionGroups'] = [{**plan['executionGroups'][0],
                                'assertionIds': ['TC-1/migrate', 'TC-1/relogin']}]
    state = runtime.initialize(plan, root)
    first = runtime.evaluate(plan, state, root)
    assert [a['id'] for a in first['nextActions']] == ['TC-1/migrate']
    assert first['dispatchGroups'][0]['assertionIds'] == ['TC-1/migrate', 'TC-1/relogin']
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    second = runtime.evaluate(plan, state, root)
    assert [a['id'] for a in second['nextActions']] == ['TC-1/relogin']
    assert second['fullyAccepted'] is False


def test_independent_groups_dispatch_together_and_later_batch_waits(runtime, scheduled):
    plan, root = scheduled
    plan['assertions'][1].update(phase=0, dependsOn=[])
    plan['executionGroups'][1].update(owner='tester-b', resources=[{'id': 'unity-b', 'access': 'write'}])
    state = runtime.initialize(plan, root)
    assert len(runtime.evaluate(plan, state, root)['dispatchGroups']) == 2
    plan['executionGroups'][1]['batch'] = 1
    state = runtime.initialize(plan, root)
    result = runtime.evaluate(plan, state, root)
    assert [a['id'] for a in result['nextActions']] == ['TC-1/migrate']
    assert [a['id'] for a in result['deferredActions']] == ['TC-1/relogin']
    state['results']['TC-1/migrate'] = {'status': 'failed', 'observation': '迁移失败', 'evidence': evidence('server')}
    assert [a['id'] for a in runtime.evaluate(plan, state, root)['nextActions']] == ['TC-1/relogin']


def test_future_phase_is_not_dispatched_before_time_gate(runtime, scheduled):
    plan, root = scheduled
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    assert runtime.evaluate(plan, state, root)['nextActions'] == []
    runtime.check_advance(plan, state, root, 1)
    state['currentPhase'] = 1
    assert [a['id'] for a in runtime.evaluate(plan, state, root)['nextActions']] == ['TC-1/relogin']


@pytest.mark.parametrize('mutation,error', [
    (lambda p: p.update(schemaVersion=1), 'PLANNING_REQUIRES_SCHEMA_2'),
    (lambda p: p.update(acceptanceMode='auto'), 'ACCEPTANCE_MODE_INVALID'),
    (lambda p: p['documentBaseline'].update(evidence=[]), 'EVIDENCE_REQUIRED'),
    (lambda p: p['executionGroups'].pop(), 'GROUP_COVERAGE'),
    (lambda p: p['executionGroups'][1].update(assertionIds=['TC-1/migrate']), 'GROUP_COVERAGE'),
    (lambda p: (p['assertions'][1].update(phase=0, dependsOn=[]), p['executionGroups'][1].update(owner='tester-b')), 'PARALLEL_RESOURCE_CONFLICT'),
    (lambda p: (p['assertions'][1].update(phase=0, dependsOn=[]), p['executionGroups'][1].update(resources=[{'id':'unity-b','access':'write'}])), 'PARALLEL_OWNER_CONFLICT'),
    (lambda p: (p['assertions'][1].update(phase=0), p['executionGroups'][0].update(batch=1)), 'DEPENDENCY_SCHEDULE_INVALID'),
])
def test_invalid_execution_plans_are_rejected(runtime, scheduled, mutation, error):
    plan, root = scheduled
    mutation(plan)
    with pytest.raises(runtime.RuntimeContractError, match=error):
        runtime.initialize(plan, root)


def test_schedule_cli_prints_reviewable_plan_without_creating_state(scheduled):
    import subprocess
    import sys
    plan, root = scheduled
    (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    result = subprocess.run([sys.executable, str(SCRIPT), 'schedule', '--plan', str(root / 'plan.json')],
                            capture_output=True, encoding='utf-8')
    assert result.returncode == 0, result.stdout + result.stderr
    output = json.loads(result.stdout)
    assert output['acceptanceMode'] == 'development'
    assert [g['id'] for g in output['executionGroups']] == ['enter', 'relogin']
    assert not (root / 'state.json').exists()


def test_shared_readers_can_parallelize_but_writer_must_wait(runtime, scheduled):
    plan, root = scheduled
    plan['assertions'][1].update(phase=0, dependsOn=[])
    plan['executionGroups'][1]['owner'] = 'tester-b'
    for group in plan['executionGroups']:
        group['resources'] = [{'id': 'server-clock', 'access': 'read'}]
    state = runtime.initialize(plan, root)
    assert len(runtime.evaluate(plan, state, root)['dispatchGroups']) == 2
    plan['executionGroups'][1]['resources'][0]['access'] = 'write'
    with pytest.raises(runtime.RuntimeContractError, match='PARALLEL_RESOURCE_CONFLICT'):
        runtime.initialize(plan, root)


def test_different_document_source_cannot_reuse_confirmation(runtime, scheduled):
    plan, root = scheduled
    baseline = json.loads((root / 'baseline.json').read_text(encoding='utf-8'))
    baseline['metadata']['documentSource'] = 'different-design-doc'
    (root / 'baseline.json').write_text(json.dumps(baseline), encoding='utf-8')
    plan['baselineSha256'] = hashlib.sha256((root / 'baseline.json').read_bytes()).hexdigest()
    with pytest.raises(runtime.RuntimeContractError, match='DOCUMENT_SOURCE_MISMATCH'):
        runtime.initialize(plan, root)


def test_missed_window_does_not_freeze_later_phases_but_denies_full_acceptance(runtime, scheduled):
    plan, root = scheduled
    plan['assertions'][1]['dependsOn'] = []
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'missed', 'reason': '活动窗口已过',
                                     'responsibility': '执行遗漏', 'nextAction': '下一期活动补验'}
    assert runtime.check_advance(plan, state, root, 1)['allowed'] is True
    state['currentPhase'] = 1
    assert [a['id'] for a in runtime.evaluate(plan, state, root)['nextActions']] == ['TC-1/relogin']
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    result = runtime.evaluate(plan, state, root)
    assert result['canFinalize'] is True and result['fullyAccepted'] is False


def test_unresolved_blocker_still_refuses_time_advance(runtime, scheduled):
    plan, root = scheduled
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'blocked', 'blocker': {
        'kind': 'permission', 'reason': '无迁移权限', 'attempts': [{'action': '申请权限', 'outcome': '被拒绝'}],
        'nextAction': '等待授权', 'options': {}}}
    with pytest.raises(runtime.RuntimeContractError, match='PHASE_INCOMPLETE:TC-1/migrate'):
        runtime.check_advance(plan, state, root, 1)


def test_reopened_earlier_phase_is_dispatched_after_time_advanced(runtime, scheduled):
    plan, root = scheduled
    plan['assertions'][1]['dependsOn'] = []
    state = runtime.initialize(plan, root)
    state['results']['TC-1/migrate'] = {'status': 'failed', 'observation': '未落地', 'evidence': evidence('server')}
    runtime.check_advance(plan, state, root, 1)
    state['currentPhase'] = 1
    state['results']['TC-1/migrate'] = {'status': 'pending', 'nextAction': '修复部署后复测迁移'}
    result = runtime.evaluate(plan, state, root)
    assert [a['action'] for a in result['nextActions']] == ['修复部署后复测迁移']
    assert [a['id'] for a in result['deferredActions']] == ['TC-1/relogin']
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    assert [a['id'] for a in runtime.evaluate(plan, state, root)['nextActions']] == ['TC-1/relogin']


def run_cli(*args):
    import subprocess
    import sys
    result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, encoding='utf-8')
    return result.returncode, json.loads(result.stdout)


def test_record_cli_validates_before_saving_and_gates_phase(scheduled):
    plan, root = scheduled
    files = {'plan': root / 'plan.json', 'state': root / 'state.json', 'patch': root / 'patch.json'}
    files['plan'].write_text(json.dumps(plan), encoding='utf-8')
    assert run_cli('init', '--plan', files['plan'], '--state', files['state'])[0] == 0
    before = files['state'].read_text(encoding='utf-8')

    def record(patch):
        files['patch'].write_text(json.dumps(patch), encoding='utf-8')
        return run_cli('record', '--plan', files['plan'], '--state', files['state'], '--patch', files['patch'])

    code, output = record({'results': {'TC-1/migrate': {'status': 'passed', 'observation': '只有截图'}}})
    assert code == 1 and output['error'] == 'OBSERVATION_REQUIRED:TC-1/migrate'
    code, output = record({'results': {'TC-9': {'status': 'pending'}}})
    assert code == 1 and output['error'] == 'PATCH_ASSERTION_UNKNOWN:TC-9'
    code, output = record({'currentPhase': 1})
    assert code == 1 and output['error'].startswith('PHASE_INCOMPLETE')
    assert files['state'].read_text(encoding='utf-8') == before

    code, output = record({'results': {'TC-1/migrate': {'status': 'passed', 'observation': '权威状态已核对',
                                                       'evidence': evidence('protocol', 'server')}},
                           'currentPhase': 1})
    assert code == 0 and [a['id'] for a in output['nextActions']] == ['TC-1/relogin']
    saved = json.loads(files['state'].read_text(encoding='utf-8'))
    assert saved['currentPhase'] == 1 and saved['results']['TC-1/migrate']['status'] == 'passed'
    assert [p.name for p in root.iterdir() if p.name.endswith('.tmp')] == []


def test_cli_names_the_assertion_and_field_behind_a_malformed_plan(scheduled):
    plan, root = scheduled
    del plan['assertions'][1]['testcaseId']
    (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    code, output = run_cli('schedule', '--plan', root / 'plan.json')
    assert code == 1 and 'TC-1/relogin' in output['error'] and 'testcaseId' in output['error']
    del plan['baselineFile']
    (root / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    code, output = run_cli('schedule', '--plan', root / 'plan.json')
    assert code == 1 and output['error'] == 'KeyError' and 'baselineFile' in output['detail']


def test_single_client_path_pass_is_reported_as_limited_conclusion(runtime, scheduled):
    plan, root = scheduled
    plan['clientPaths'] = {'unity': 'in_scope', 'device': 'out_of_scope'}
    for a in plan['assertions']:
        a['clientPath'] = 'unity'
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    result = runtime.publish(plan, state, root, root / 'report')
    assert result['fullyAccepted'] is True and result['stageFullyAccepted'] is False
    assert result['clientPaths']['device'] == {'scope': 'out_of_scope', 'counts': {}, 'allPassed': False}
    report = (root / 'report/summary.html').read_text(encoding='utf-8')
    assert '（仅Unity路径）通过' in report and '本轮范围外（未验收）' in report and '环境与收尾证据' in report
    assert [p.name for p in root.iterdir() if 'partial' in p.name] == []


def test_both_client_paths_passing_gives_complete_stage_conclusion(runtime, scheduled):
    plan, root = scheduled
    plan['clientPaths'] = {'unity': 'in_scope', 'device': 'in_scope'}
    plan['assertions'][0]['clientPath'] = 'unity'
    plan['assertions'][1]['clientPath'] = 'device'
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    assert runtime.evaluate(plan, state, root)['stageFullyAccepted'] is True


@pytest.mark.parametrize('paths,tags,error', [
    ({'unity': 'in_scope', 'device': 'in_scope'}, ['unity', 'unity'], 'CLIENT_PATH_UNCOVERED:device'),
    ({'unity': 'in_scope', 'device': 'out_of_scope'}, ['unity', 'device'], 'CLIENT_PATH_OUT_OF_SCOPE:TC-1/relogin'),
    ({'unity': 'in_scope', 'device': 'out_of_scope'}, ['unity', None], 'CLIENT_PATH_INVALID:TC-1/relogin'),
    ({'unity': 'out_of_scope', 'device': 'out_of_scope'}, [None, None], 'CLIENT_PATHS_INVALID'),
    (None, ['unity', None], 'CLIENT_PATHS_REQUIRED'),
])
def test_client_path_scope_must_match_assertions(runtime, scheduled, paths, tags, error):
    plan, root = scheduled
    if paths is not None:
        plan['clientPaths'] = paths
    for a, tag in zip(plan['assertions'], tags):
        if tag:
            a['clientPath'] = tag
    with pytest.raises(runtime.RuntimeContractError, match=error):
        runtime.initialize(plan, root)


def test_publish_refuses_to_overwrite_existing_report(runtime, scheduled):
    plan, root = scheduled
    state = runtime.initialize(plan, root)
    passed(state, 'TC-1/migrate', 'protocol', 'server')
    passed(state, 'TC-1/relogin', 'runtime')
    finish(state)
    (root / 'report').mkdir()
    with pytest.raises(runtime.RuntimeContractError, match='OUTPUT_ALREADY_EXISTS'):
        runtime.publish(plan, state, root, root / 'report')
    assert list((root / 'report').iterdir()) == []
