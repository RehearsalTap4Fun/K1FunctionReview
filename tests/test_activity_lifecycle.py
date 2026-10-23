from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from lifecycle_fixtures import valid_payload, run_renderer, reports_root

ROOT = Path(__file__).resolve().parents[1]
STAGES = ['start', 'active', 'end', 'settlement', 'recovery', 'close', 'next_cycle']
OBSERVABLES = {
    'rank_reward': ['mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'],
    'unclaimed_reward': ['eligibility', 'mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'],
    'peripheral_reward': ['eligibility', 'mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'],
    'asset_recovery': ['before_after_inventory', 'late_delivery'],
    'progress_cleanup': ['before_after_progress', 'next_cycle'],
    'unfinished_round': ['result_state', 'no_new_rewards'],
}


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'review-k1-function/scripts' / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def lifecycle(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'review-k1-function/scripts'))
    return module('activity_lifecycle')


def activity_payload():
    p = valid_payload()
    p['metadata']['featureType'] = 'activity'
    rids = [r['id'] for r in p['requirements']]
    tids = [c['id'] for c in p['testcases']]
    case_by_id = {c['id']: c for c in p['testcases']}
    p['activityLifecycle'] = {
        'schemaVersion': 1,
        'stages': [{'id': s, 'status': 'unknown', 'requirementIds': rids,
                    'reason': '需要追踪冻结实现中的该阶段，补验台账明确承接'} for s in STAGES],
        'assertions': [{'id': 'END-' + k, 'kind': k, 'applicability': 'required',
                        'requirementIds': case_by_id[tids[i % len(tids)]]['requirementIds'],
                        'testcaseIds': [tids[i % len(tids)]],
                        'expected': '按已确认规则核对 ' + k, 'action': '执行独立场景并读取权威结果 ' + k,
                        'observables': v, 'requiredEvidence': ['server']}
                       for i, (k, v) in enumerate(OBSERVABLES.items())],
    }
    sources = ['stage:' + s for s in STAGES]
    sources += ['requirement:' + r['id'] for r in p['requirements'] if r['result'] != '静态证据充分']
    sources += ['finding:' + f['id'] for f in p['findings']]
    p['followupObligations'] = [{'id': 'O-' + str(i), 'sourceRefs': [s], 'requirementIds': rids,
                                'assertionIds': [a['id'] for a in p['activityLifecycle']['assertions']],
                                'nextAction': '执行对应独立断言，回读权威结果',
                                'closureCriteria': '每项副作用及异常分支有结果和证据'} for i, s in enumerate(sources)]
    return p


def test_activity_report_without_contract_is_rejected_by_existing_entrypoint(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'review-k1-function/scripts'))
    renderer = module('render-fast-precheck')
    p = valid_payload()
    p['metadata']['featureType'] = 'activity'
    with pytest.raises(ValueError, match='ACTIVITY_LIFECYCLE_REQUIRED'):
        renderer.validate_payload(p)


def test_non_activity_and_single_round_settlement_remain_compatible(lifecycle):
    p = valid_payload()
    p['requirements'][0]['expectation'] = '单局结算奖励显示'
    assert not lifecycle.is_activity(p)
    lifecycle.validate_lifecycle(p)


def test_unknown_stages_can_publish_only_with_explicit_followups(lifecycle):
    p = activity_payload()
    lifecycle.validate_lifecycle(p)
    p['followupObligations'] = []
    with pytest.raises(ValueError, match='FOLLOWUP_SOURCE_UNCOVERED'):
        lifecycle.validate_lifecycle(p)


@pytest.mark.parametrize('stage', STAGES)
def test_no_lifecycle_stage_can_disappear(lifecycle, stage):
    p = activity_payload()
    p['activityLifecycle']['stages'] = [s for s in p['activityLifecycle']['stages'] if s['id'] != stage]
    with pytest.raises(ValueError, match='LIFECYCLE_STAGE_COVERAGE'):
        lifecycle.validate_lifecycle(p)


@pytest.mark.parametrize('kind', list(OBSERVABLES))
def test_side_effects_cannot_be_merged_into_one_generic_end_assertion(lifecycle, kind):
    p = activity_payload()
    p['activityLifecycle']['assertions'] = [a for a in p['activityLifecycle']['assertions'] if a['kind'] != kind]
    with pytest.raises(ValueError, match='SETTLEMENT_ASSERTION_COVERAGE'):
        lifecycle.validate_lifecycle(p)


def test_state_only_assertion_cannot_prove_mail_delivery(lifecycle):
    p = activity_payload()
    p['activityLifecycle']['assertions'][0]['observables'] = ['result_state']
    with pytest.raises(ValueError, match='SETTLEMENT_OBSERVABLES_MISSING'):
        lifecycle.validate_lifecycle(p)


def test_not_applicable_requires_document_basis(lifecycle):
    p = activity_payload()
    p['activityLifecycle']['stages'][0] = {'id': 'start', 'status': 'not_applicable', 'reason': '不验'}
    with pytest.raises(ValueError, match='APPLICABILITY_BASIS_REQUIRED'):
        lifecycle.validate_lifecycle(p)


def test_checked_cleanup_requires_chain_not_only_onend(lifecycle):
    p = activity_payload()
    p['activityLifecycle']['stages'][5] = {
        'id': 'close', 'status': 'checked', 'requirementIds': ['REQ-03'],
        'reason': 'OnEnd存在', 'chain': [{'step': 'trigger', 'evidenceRefs': [{'requirementId': 'REQ-03', 'index': 0}],
                                        'explanation': '只找到转调入口'}]}
    with pytest.raises(ValueError, match='LIFECYCLE_CHAIN_INCOMPLETE'):
        lifecycle.validate_lifecycle(p)


def test_same_entrypoint_with_trailing_newline_is_one_anchor(lifecycle):
    p = activity_payload()
    ev = p['requirements'][2]['evidence'][0]
    ev['snippet'] = 'func OnEnd() { sendRewards() }'
    p['requirements'][2]['evidence'].append(dict(ev, snippet=ev['snippet'] + '\n'))
    p['followupObligations'] = [o for o in p['followupObligations'] if 'stage:close' not in o['sourceRefs']]
    p['activityLifecycle']['stages'][5] = {
        'id': 'close', 'status': 'checked', 'requirementIds': ['REQ-03'], 'reason': '只定位到入口',
        'chain': [{'step': s, 'explanation': '入口调用',
                   'evidenceRefs': [{'requirementId': 'REQ-03', 'index': i % 2}]}
                  for i, s in enumerate(['trigger', 'effect', 'persistence'])]}
    with pytest.raises(ValueError, match='LIFECYCLE_ENTRYPOINT_ONLY'):
        lifecycle.validate_lifecycle(p)


def test_one_assertion_cannot_hide_multiple_case_scenarios(lifecycle):
    p = activity_payload()
    p['activityLifecycle']['assertions'][0]['testcaseIds'] = [c['id'] for c in p['testcases']]
    p['activityLifecycle']['assertions'][0]['requirementIds'] = [r['id'] for r in p['requirements']]
    with pytest.raises(ValueError, match='SETTLEMENT_ASSERTION_SINGLE_CASE_REQUIRED'):
        lifecycle.validate_lifecycle(p)


def test_non_sufficient_requirement_and_risk_cannot_leave_followup_queue(lifecycle):
    for source in ['requirement:REQ-03', 'finding:FIND-02']:
        p = activity_payload()
        p['followupObligations'] = [o for o in p['followupObligations'] if source not in o['sourceRefs']]
        with pytest.raises(ValueError, match='FOLLOWUP_SOURCE_UNCOVERED'):
            lifecycle.validate_lifecycle(p)


def test_historical_end_reward_text_triggers_all_four_rules(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'review-k1-function/scripts'))
    matcher = module('review_rule_matcher')
    p = valid_payload()
    p['requirements'] = [deepcopy(p['requirements'][2])]
    p['requirements'][0].update(title='结束补发', expectation='达到档位后可领取对应奖励；未领取的，活动结束时邮件补发。')
    p['requirements'][0]['evidence'][0]['path'] = 'game/actv/template/reward.go'
    git = {'schemaVersion': 1, 'status': 'ok', 'repositories': [
        {'role': r['role'], 'target': {'sha': r['target']}, 'changes': []} for r in p['metadata']['repositories']]}
    rules = json.loads((ROOT / 'review-k1-function/references/k1-review-rules.json').read_text(encoding='utf-8'))
    selected = {r['ruleId'] for r in matcher.resolve_rules(rules, p, git)['selectedRules']}
    assert {'server.time-boundary', 'server.state-transition', 'server.persistence', 'server.idempotence'} <= selected


def test_real_gold_miner_history_requires_migration(monkeypatch):
    path = ROOT / '.tmp/gold-miner-alignment-20261013-01/precheck-20261013/result.json'
    if not path.exists():
        pytest.skip('Private historical artifact is not included in shared skill')
    monkeypatch.syspath_prepend(str(ROOT / 'review-k1-function/scripts'))
    p = json.loads(path.read_text(encoding='utf-8-sig'))
    assert any(t['id'] == 'GM-TC-076' for t in p['testcases'])
    assert any(f['id'] == 'F-022' for f in p['findings'])
    with pytest.raises(ValueError, match='ACTIVITY_LIFECYCLE_REQUIRED'):
        module('render-fast-precheck').validate_payload(p)


def test_missing_contract_refuses_cli_publication_without_report(project_tmp, reports_root):
    p = valid_payload()
    p['metadata']['featureType'] = 'activity'
    result = run_renderer(project_tmp, reports_root, p)
    assert result.returncode != 0
    assert 'ACTIVITY_LIFECYCLE_REQUIRED' in result.stdout + result.stderr
    assert not list(reports_root.iterdir())


def test_unknown_lifecycle_and_followups_are_visible_in_published_report(project_tmp, reports_root):
    result = run_renderer(project_tmp, reports_root, activity_payload())
    assert result.returncode == 0, result.stdout + result.stderr
    directory = Path(json.loads(result.stdout)['directory'])
    for name in ['review.md', 'summary.html']:
        rendered = (directory / name).read_text(encoding='utf-8')
        assert 'stage:settlement' in rendered
        assert 'END-rank_reward' in rendered
        assert 'unknown' in rendered
        assert '待补验' in rendered


def test_external_correction_obligation_cannot_disappear(lifecycle):
    p = activity_payload()
    p['followupSources'] = [{'id': 'DEV-CHK-012', 'requirementIds': ['REQ-03'], 'description': '更正后的开发文档保留的未决义务'}]
    with pytest.raises(ValueError, match='FOLLOWUP_SOURCE_UNCOVERED:external:DEV-CHK-012'):
        lifecycle.validate_lifecycle(p)
    p['followupObligations'][0]['sourceRefs'].append('external:DEV-CHK-012')
    lifecycle.validate_lifecycle(p)


def test_template_is_coherent_when_placeholder_ids_are_bound(lifecycle):
    p = json.loads((ROOT / 'review-k1-function/assets/activity-lifecycle.json').read_text(encoding='utf-8'))
    p['metadata'] = {'featureType': 'activity'}
    p['requirements'] = [{'id': 'REQ-ACTIVITY-END', 'result': '无法确认'}]
    p['testcases'] = [{'id': a['testcaseIds'][0], 'requirementIds': a['requirementIds']}
                      for a in p['activityLifecycle']['assertions']]
    lifecycle.validate_lifecycle(p)


def test_complete_distinct_code_chain_is_accepted(lifecycle):
    p = activity_payload()
    ev = p['requirements'][2]['evidence'][0]
    ev['snippet'] = 'onClose()'
    p['requirements'][2]['evidence'].append(dict(ev, snippet='deleteAndPersist()'))
    p['followupObligations'] = [o for o in p['followupObligations'] if 'stage:close' not in o['sourceRefs']]
    p['activityLifecycle']['stages'][5] = {
        'id': 'close', 'status': 'checked', 'requirementIds': ['REQ-03'], 'reason': '关闭调用数据清理并落库',
        'chain': [{'step': s, 'explanation': '已追踪冻结版本代码',
                   'evidenceRefs': [{'requirementId': 'REQ-03', 'index': min(i, 1)}]}
                  for i, s in enumerate(['trigger', 'effect', 'persistence'])]}
    lifecycle.validate_lifecycle(p)
