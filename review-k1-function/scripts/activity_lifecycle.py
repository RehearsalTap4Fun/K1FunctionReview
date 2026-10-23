"""Activity coverage contracts shared by static publication and runtime handoff.

These gates validate traceability, not the truth of a business observation.
Evidence references reuse the frozen anchors verified by evidence_anchors.py.
"""
from __future__ import annotations

import re


class LifecycleError(ValueError):
    pass


STAGE_STEPS = {
    'start': ('trigger', 'handler', 'effect'),
    'active': ('handler', 'guard', 'effect'),
    'end': ('trigger', 'handler', 'guard'),
    'settlement': ('trigger', 'handler', 'dispatch', 'effect', 'persistence', 'failure'),
    'recovery': ('handler', 'effect', 'persistence', 'failure'),
    'close': ('trigger', 'effect', 'persistence'),
    'next_cycle': ('trigger', 'guard', 'effect'),
}
OBSERVABLES = {
    'rank_reward': {'mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'},
    'unclaimed_reward': {'eligibility', 'mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'},
    'peripheral_reward': {'eligibility', 'mail_count', 'attachments', 'asset_delta', 'duplicate_delivery'},
    'asset_recovery': {'before_after_inventory', 'late_delivery'},
    'progress_cleanup': {'before_after_progress', 'next_cycle'},
    'unfinished_round': {'result_state', 'no_new_rewards'},
}
RUNTIME_KINDS = {'server', 'runtime', 'protocol', 'platform'}


def require(ok, code):
    if not ok:
        raise LifecycleError(code)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def identifiers(value, code, *, empty=False):
    require(isinstance(value, list) and (empty or bool(value)), code)
    require(all(text(x) for x in value) and len(set(value)) == len(value), code)
    return set(value)


def indexed(value, code):
    require(isinstance(value, list), code)
    result = {}
    for item in value:
        require(isinstance(item, dict) and text(item.get('id')), code)
        require(item['id'] not in result, code)
        result[item['id']] = item
    return result


def requirement_text(r):
    return '\n'.join(str(r.get(k, '')) for k in ('title', 'documentLocator', 'expectation', 'expected', 'source'))


def is_activity(payload):
    metadata = payload.get('metadata', {})
    if 'activityLifecycle' in payload or metadata.get('featureType') == 'activity':
        return True
    content = str(metadata.get('feature', '')) + '\n' + '\n'.join(
        requirement_text(r) for r in payload.get('requirements', []) + payload.get('testcases', []))
    if '活动' in content or re.search(r'\bactivity\b', content, re.I):
        return True
    return any(re.search(r'(?:^|/)(?:actv|activity)(?:/|[^/]*\.xlsx$)', e.get('path', '').replace('\\', '/'), re.I)
               for r in payload.get('requirements', []) for e in r.get('evidence', []))


def lifecycle_signal(requirement, payload):
    """Semantic expansion avoids requiring the spec to literally say 'idempotent'."""
    words = requirement_text(requirement)
    if any(s in words for s in ('活动结束', '结束活动', '活动结算', '活动关闭', '活动回收', '期末', '跨期', '补发')):
        return True
    if is_activity(payload) and any(s in words for s in ('邮件发奖', '排行奖励', '清理', '下一期')):
        return True
    contract = payload.get('activityLifecycle')
    return isinstance(contract, dict) and isinstance(contract.get('stages'), list) and any(
        isinstance(s, dict) and requirement.get('id') in s.get('requirementIds', [])
        for s in contract.get('stages', []))


def applicability_basis(item):
    require(text(item.get('reason')) and text(item.get('documentLocator')), 'APPLICABILITY_BASIS_REQUIRED')


def validate_lifecycle(payload):
    if not is_activity(payload):
        require('followupObligations' not in payload, 'FOLLOWUP_WITHOUT_LIFECYCLE')
        return None
    contract = payload.get('activityLifecycle')
    require(isinstance(contract, dict) and contract.get('schemaVersion') == 1, 'ACTIVITY_LIFECYCLE_REQUIRED')
    requirements = indexed(payload.get('requirements'), 'LIFECYCLE_REQUIREMENTS_REQUIRED')
    cases = indexed(payload.get('testcases'), 'LIFECYCLE_CASES_REQUIRED')
    findings = indexed(payload.get('findings', []), 'LIFECYCLE_FINDINGS_INVALID')
    sources = {'requirement:' + r['id']: {r['id']} for r in requirements.values() if r.get('result') != '静态证据充分'}
    sources.update({'finding:' + f['id']: set(f.get('requirementIds', [])) for f in findings.values()})
    for source in indexed(payload.get('followupSources', []), 'FOLLOWUP_SOURCES_INVALID').values():
        refs = identifiers(source.get('requirementIds'), 'FOLLOWUP_REQUIREMENTS_INVALID')
        require(refs <= requirements.keys() and text(source.get('description')), 'FOLLOWUP_SOURCES_INVALID')
        sources['external:' + source['id']] = refs

    def req_refs(item):
        refs = identifiers(item.get('requirementIds'), 'LIFECYCLE_REQUIREMENT_REFERENCE_INVALID')
        require(refs <= requirements.keys(), 'LIFECYCLE_REQUIREMENT_REFERENCE_INVALID')
        return refs

    stages = indexed(contract.get('stages'), 'LIFECYCLE_STAGE_COVERAGE')
    require(stages.keys() == STAGE_STEPS.keys(), 'LIFECYCLE_STAGE_COVERAGE')
    for stage in stages.values():
        state = stage.get('status')
        require(state in {'checked', 'unknown', 'not_applicable'}, 'LIFECYCLE_STAGE_STATUS_INVALID')
        if state == 'not_applicable':
            applicability_basis(stage)
            require(not stage.get('chain'), 'NOT_APPLICABLE_WITH_CHAIN')
            continue
        refs = req_refs(stage)
        require(text(stage.get('reason')), 'LIFECYCLE_STAGE_REASON_REQUIRED')
        if state == 'unknown':
            sources['stage:' + stage['id']] = refs
            continue
        chain = stage.get('chain')
        require(isinstance(chain, list) and all(isinstance(s, dict) for s in chain), 'LIFECYCLE_CHAIN_INCOMPLETE')
        require(len(chain) == len(STAGE_STEPS[stage['id']]) and {s.get('step') for s in chain} == set(STAGE_STEPS[stage['id']]),
                'LIFECYCLE_CHAIN_INCOMPLETE')
        anchors = set()
        for step in chain:
            require(text(step.get('explanation')), 'LIFECYCLE_CHAIN_EXPLANATION_REQUIRED')
            refs_e = step.get('evidenceRefs')
            require(isinstance(refs_e, list) and bool(refs_e), 'LIFECYCLE_CHAIN_EVIDENCE_REQUIRED')
            for ref in refs_e:
                require(isinstance(ref, dict) and ref.get('requirementId') in refs and type(ref.get('index')) is int,
                        'LIFECYCLE_ANCHOR_REFERENCE_INVALID')
                ev = requirements[ref['requirementId']].get('evidence', [])
                require(0 <= ref['index'] < len(ev), 'LIFECYCLE_ANCHOR_REFERENCE_INVALID')
                e = ev[ref['index']]
                require(e.get('repository') == 'server' and text(e.get('snippet')) and not e.get('unverifiedReason')
                        and not e.get('path', '').lower().endswith('.xlsx'), 'LIFECYCLE_CODE_EVIDENCE_REQUIRED')
                # Match evidence_anchors.locate normalization so a trailing newline
                # or Windows line endings cannot manufacture a second code anchor.
                snippet = tuple(e['snippet'].replace('\r\n', '\n').removesuffix('\n').split('\n'))
                anchors.add((e.get('ref'), e.get('path', '').replace('\\', '/'), snippet))
        require(len(anchors) >= 2, 'LIFECYCLE_ENTRYPOINT_ONLY')

    assertions = indexed(contract.get('assertions'), 'SETTLEMENT_ASSERTION_COVERAGE')
    kinds_present = {a.get('kind') for a in assertions.values()}
    require(OBSERVABLES.keys() <= kinds_present <= OBSERVABLES.keys() | {'requirement'}, 'SETTLEMENT_ASSERTION_COVERAGE')
    required = {}
    for a in assertions.values():
        require(a.get('applicability') in {'required', 'not_applicable'}, 'SETTLEMENT_APPLICABILITY_INVALID')
        if a['applicability'] == 'not_applicable':
            require(a['kind'] != 'requirement', 'GENERAL_ASSERTION_MUST_BE_REQUIRED')
            applicability_basis(a)
            require(not a.get('testcaseIds'), 'NOT_APPLICABLE_WITH_TESTCASES')
            require(sum(x['kind'] == a['kind'] for x in assertions.values()) == 1, 'CONFLICTING_ASSERTION_APPLICABILITY')
            continue
        refs = req_refs(a)
        tids = identifiers(a.get('testcaseIds'), 'SETTLEMENT_TESTCASE_REFERENCE_INVALID')
        require(len(tids) == 1, 'SETTLEMENT_ASSERTION_SINGLE_CASE_REQUIRED')
        require(tids <= cases.keys(), 'SETTLEMENT_TESTCASE_REFERENCE_INVALID')
        require(all(set(cases[t].get('requirementIds', [])) & refs for t in tids)
                and refs <= set().union(*(set(cases[t].get('requirementIds', [])) for t in tids)),
                'SETTLEMENT_REQUIREMENT_CASE_MISMATCH')
        require(text(a.get('expected')) and text(a.get('action')), 'SETTLEMENT_ASSERTION_INVALID')
        obs = identifiers(a.get('observables'), 'SETTLEMENT_OBSERVABLES_MISSING')
        require(OBSERVABLES.get(a['kind'], set()) <= obs, 'SETTLEMENT_OBSERVABLES_MISSING:' + a['id'])
        kinds = identifiers(a.get('requiredEvidence'), 'SETTLEMENT_RUNTIME_EVIDENCE_REQUIRED')
        authoritative = RUNTIME_KINDS | {'ui'} if a['kind'] == 'requirement' else {'server', 'runtime', 'platform'}
        require(kinds <= RUNTIME_KINDS | {'ui'} and bool(kinds & authoritative),
                'SETTLEMENT_RUNTIME_EVIDENCE_REQUIRED')
        required[a['id']] = a

    obligations = indexed(payload.get('followupObligations', []), 'FOLLOWUP_OBLIGATIONS_INVALID')
    covered = set()
    for o in obligations.values():
        refs = req_refs(o)
        source_refs = identifiers(o.get('sourceRefs'), 'FOLLOWUP_SOURCE_INVALID')
        require(source_refs <= sources.keys(), 'FOLLOWUP_SOURCE_INVALID')
        require(set().union(*(sources[s] for s in source_refs)) <= refs, 'FOLLOWUP_SOURCE_REQUIREMENT_MISMATCH')
        aids = identifiers(o.get('assertionIds'), 'FOLLOWUP_ASSERTION_REFERENCE_INVALID')
        require(aids <= required.keys(), 'FOLLOWUP_ASSERTION_REFERENCE_INVALID')
        require(refs <= set().union(*(set(required[a]['requirementIds']) for a in aids)), 'FOLLOWUP_ASSERTION_REQUIREMENT_MISMATCH')
        require(text(o.get('nextAction')) and text(o.get('closureCriteria')), 'FOLLOWUP_CLOSURE_REQUIRED')
        covered.update(source_refs)
    require(covered == sources.keys(), 'FOLLOWUP_SOURCE_UNCOVERED:' + ','.join(sorted(sources.keys() - covered)))
    return contract


def validate_runtime_handoff(baseline, plan):
    contract = validate_lifecycle(baseline)
    if contract is None:
        return {}
    required = {a['id']: a for a in contract['assertions'] if a['applicability'] == 'required'}
    bindings = {}
    for a in plan['assertions']:
        key = a.get('lifecycleAssertionId')
        if key is None:
            continue
        require(key in required and key not in bindings, 'LIFECYCLE_RUNTIME_BINDING_INVALID')
        spec = required[key]
        require(a['testcaseId'] in spec['testcaseIds'], 'LIFECYCLE_RUNTIME_CASE_MISMATCH')
        require(a['expected'] == spec['expected'] and a['action'] == spec['action'], 'LIFECYCLE_RUNTIME_EXPECTATION_CHANGED')
        require(set(spec['requiredEvidence']) <= set(a['requiredEvidence']), 'LIFECYCLE_RUNTIME_EVIDENCE_WEAKENED')
        bindings[key] = a['id']
    require(bindings.keys() == required.keys(), 'LIFECYCLE_RUNTIME_ASSERTION_MISSING')
    return bindings


def validate_runtime_observations(baseline, plan, state, root, evidence_kinds):
    bindings = validate_runtime_handoff(baseline, plan)
    if not bindings:
        return {}
    specifications = {a['id']: a for a in baseline['activityLifecycle']['assertions']}
    for spec_id, aid in bindings.items():
        r = state['results'][aid]
        if r['status'] != 'passed':
            continue
        observed = r.get('observedEffects', {})
        require(isinstance(observed, dict), 'SETTLEMENT_OBSERVATIONS_REQUIRED')
        spec = specifications[spec_id]
        for observable in spec['observables']:
            entry = observed.get(observable)
            require(isinstance(entry, dict) and text(entry.get('observation')), 'SETTLEMENT_OBSERVATIONS_REQUIRED:' + observable)
            kinds = evidence_kinds(entry.get('evidence', []), root, required=True)
            allowed = RUNTIME_KINDS | {'ui'} if spec['kind'] == 'requirement' else {'server', 'runtime', 'platform'}
            require(bool(kinds & allowed) and set(spec['requiredEvidence']) <= kinds,
                    'SETTLEMENT_OBSERVATION_NOT_RUNTIME')
    outcomes = {}
    for o in baseline.get('followupObligations', []):
        statuses = [state['results'][bindings[a]]['status'] for a in o['assertionIds']]
        outcomes[o['id']] = {'status': 'verified' if all(s == 'passed' for s in statuses) else 'open',
                             'assertionIds': [bindings[a] for a in o['assertionIds']],
                             'sourceRefs': o['sourceRefs'], 'nextAction': o['nextAction'],
                             'closureCriteria': o['closureCriteria']}
    return outcomes


def lifecycle_rows(payload):
    """Presentation data only; publication validates before this is called."""
    contract = payload.get('activityLifecycle')
    if not contract:
        return []
    rows = [['阶段/' + s['id'], s['status'], s.get('reason', '')] for s in contract['stages']]
    rows += [[a['id'] + '/' + a['kind'], a['applicability'], a.get('expected', a.get('reason', ''))]
             for a in contract['assertions']]
    rows += [[o['id'], '待补验', ', '.join(o['sourceRefs']) + ' → ' + ', '.join(o['assertionIds'])
              + '；' + o['nextAction'] + '；关闭标准：' + o['closureCriteria']]
             for o in payload.get('followupObligations', [])]
    return rows
