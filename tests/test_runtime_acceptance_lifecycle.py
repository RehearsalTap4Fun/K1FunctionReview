from copy import deepcopy
import hashlib
import json

import pytest

from test_activity_lifecycle import activity_payload
from test_runtime_acceptance import runtime, evidence, finish


@pytest.fixture
def activity_sample(tmp_path):
    baseline = activity_payload()
    source = tmp_path / 'baseline.json'
    source.write_text(json.dumps(baseline), encoding='utf-8')
    (tmp_path / 'evidence.json').write_text('{"observed":"mail and inventory snapshots"}', encoding='utf-8')
    cases = [c['id'] for c in baseline['testcases']]
    plan = {'schemaVersion': 1, 'runId': 'activity-test', 'baselineFile': 'baseline.json',
            'baselineSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'assertions': [
                {'id': a['id'] + '/runtime', 'lifecycleAssertionId': a['id'],
                 'testcaseId': a['testcaseIds'][0], 'expected': a['expected'], 'action': a['action'],
                 'phase': 0, 'dependsOn': [], 'requiredEvidence': a['requiredEvidence']}
                for i, a in enumerate(baseline['activityLifecycle']['assertions'])]}
    return baseline, plan, tmp_path


def mark_all_passed(state):
    for aid in state['results']:
        state['results'][aid] = {'status': 'passed', 'observation': '状态离开 Start', 'evidence': evidence('server')}
    finish(state)


def add_effect_observations(baseline, plan, state):
    by_id = {a['id']: a for a in baseline['activityLifecycle']['assertions']}
    for a in plan['assertions']:
        state['results'][a['id']]['observedEffects'] = {
            key: {'observation': '已核对前后差值、数量和对应预期', 'evidence': evidence('server')}
            for key in by_id[a['lifecycleAssertionId']]['observables']}


def test_existing_generic_pass_cannot_publish_end_settlement(runtime, activity_sample):
    baseline, plan, root = activity_sample
    state = runtime.initialize(plan, root)
    mark_all_passed(state)
    with pytest.raises(ValueError, match='SETTLEMENT_OBSERVATIONS_REQUIRED'):
        runtime.publish(plan, state, root, root / 'report')
    assert not (root / 'report').exists()


def test_each_settlement_assertion_must_survive_runtime_handoff(runtime, activity_sample):
    _, plan, root = activity_sample
    plan['assertions'].pop()
    with pytest.raises(ValueError, match='LIFECYCLE_RUNTIME_ASSERTION_MISSING'):
        runtime.initialize(plan, root)


def test_assertion_cannot_claim_two_independent_effects(runtime, activity_sample):
    _, plan, root = activity_sample
    plan['assertions'][1]['lifecycleAssertionId'] = plan['assertions'][0]['lifecycleAssertionId']
    with pytest.raises(ValueError, match='LIFECYCLE_RUNTIME_BINDING_INVALID'):
        runtime.initialize(plan, root)


def test_changed_expected_or_weakened_evidence_is_rejected(runtime, activity_sample):
    _, original, root = activity_sample
    for field, value, code in [('expected', '活动已关闭即通过', 'EXPECTATION_CHANGED'),
                                ('requiredEvidence', ['protocol'], 'EVIDENCE_WEAKENED')]:
        plan = deepcopy(original)
        plan['assertions'][0][field] = value
        with pytest.raises(ValueError, match=code):
            runtime.initialize(plan, root)


def test_static_evidence_cannot_prove_mail_side_effect(runtime, activity_sample):
    baseline, plan, root = activity_sample
    state = runtime.initialize(plan, root)
    mark_all_passed(state)
    add_effect_observations(baseline, plan, state)
    state['results'][plan['assertions'][0]['id']]['observedEffects']['attachments']['evidence'] = evidence('static')
    with pytest.raises(ValueError, match='SETTLEMENT_OBSERVATION_NOT_RUNTIME'):
        runtime.evaluate(plan, state, root)


def test_protocol_only_effects_cannot_reuse_unrelated_server_result(runtime, activity_sample):
    baseline, plan, root = activity_sample
    state = runtime.initialize(plan, root)
    mark_all_passed(state)
    add_effect_observations(baseline, plan, state)
    for r in state['results'].values():
        for obs in r['observedEffects'].values():
            obs['evidence'] = evidence('protocol')
    with pytest.raises(ValueError, match='SETTLEMENT_OBSERVATION_NOT_RUNTIME'):
        runtime.evaluate(plan, state, root)


def test_complete_effect_evidence_closes_obligations_and_renders_queue(runtime, activity_sample):
    baseline, plan, root = activity_sample
    state = runtime.initialize(plan, root)
    mark_all_passed(state)
    add_effect_observations(baseline, plan, state)
    result = runtime.publish(plan, state, root, root / 'report')
    assert result['fullyAccepted']
    assert len(result['followupResults']) == len(baseline['followupObligations'])
    assert all(x['status'] == 'verified' for x in result['followupResults'].values())
    assert '补验义务' in (root / 'report/summary.html').read_text(encoding='utf-8')


def test_excluded_assertion_stays_open_in_followup_ledger(runtime, activity_sample):
    baseline, plan, root = activity_sample
    state = runtime.initialize(plan, root)
    mark_all_passed(state)
    add_effect_observations(baseline, plan, state)
    state['results'][plan['assertions'][0]['id']] = {
        'status': 'excluded', 'reason': '本轮只体验局内玩法', 'userDecision': '用户明确排除本轮排行邮件实测'}
    result = runtime.evaluate(plan, state, root)
    assert result['canFinalize']
    assert not result['fullyAccepted']
    assert all(x['status'] == 'open' for x in result['followupResults'].values())


def test_legacy_activity_baseline_without_contract_cannot_be_republished(runtime, activity_sample):
    baseline, plan, root = activity_sample
    del baseline['activityLifecycle']
    del baseline['followupObligations']
    source = root / plan['baselineFile']
    source.write_text(json.dumps(baseline), encoding='utf-8')
    plan['baselineSha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='ACTIVITY_LIFECYCLE_REQUIRED'):
        runtime.initialize(plan, root)
