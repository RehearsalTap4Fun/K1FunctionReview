"""Durable side-effect intents. A receipt alone never verifies the outcome."""
from copy import deepcopy
from .core import canonical_hash, now, require, redact

KINDS = {'feedback', 'fixture', 'cleanup', 'recording', 'replay', 'deployment'}


def prepare(store, kind, target, inputs):
    require(kind in KINDS, 'OPERATION_KIND')
    require(isinstance(target, dict) and isinstance(inputs, dict), 'OPERATION_INPUT')
    state = store.read()
    key = canonical_hash([state['runId'], kind, target, inputs])
    oid = key[:24]
    existing = state['operations'].get(oid)
    if existing:
        require(existing['dedupeKey'] == key, 'OPERATION_COLLISION')
        return existing
    op = {'schemaVersion': 1, 'operationId': oid, 'dedupeKey': key, 'kind': kind,
          'target': redact(deepcopy(target)), 'inputSha256': canonical_hash(inputs), 'inputs': redact(deepcopy(inputs)),
          'status': 'prepared', 'receipt': None, 'verification': None, 'attempts': 0, 'createdAt': now()}
    def change(data):
        data['operations'][oid] = op
        return data
    store.update(state['revision'], change)
    return op


def _change(store, oid, change):
    state = store.read()
    require(oid in state['operations'], 'OPERATION_NOT_FOUND')
    def mutate(data):
        op = data['operations'][oid]
        change(op)
        op['updatedAt'] = now()
        return data
    return store.update(state['revision'], mutate)['operations'][oid]


def dispatch(store, operation_id):
    op = store.read()['operations'].get(operation_id)
    require(op is not None, 'OPERATION_NOT_FOUND')
    if op['status'] == 'verified':
        return op
    def change(item):
        require(item['status'] == 'prepared', 'RECONCILE_REQUIRED')
        item['status'] = 'dispatched'; item['attempts'] += 1
        item['dispatchedAt'] = now()
    return _change(store, operation_id, change)


def record_receipt(store, operation_id, receipt):
    def change(op):
        require(op['status'] in {'dispatched', 'outcome_unknown', 'verification_pending'}, 'RECEIPT_STATE')
        require(isinstance(receipt, dict), 'RECEIPT_INVALID')
        op['receipt'] = redact(deepcopy(receipt))
        op['status'] = 'verification_pending'
    return _change(store, operation_id, change)


def mark_unknown(store, operation_id, reason):
    def change(op):
        require(op['status'] in {'dispatched', 'verification_pending'}, 'UNKNOWN_STATE')
        op['status'] = 'outcome_unknown'; op['unknownReason'] = str(reason)
    return _change(store, operation_id, change)


def complete_verification(store, operation_id, validation):
    """Internal adapter API; the CLI cannot submit arbitrary verification flags."""
    def change(op):
        require(op['status'] in {'dispatched', 'verification_pending', 'outcome_unknown'}, 'VERIFICATION_STATE')
        require(validation.get('status') in {'verified', 'mismatch', 'incomplete'}, 'VERIFICATION_INVALID')
        require(isinstance(validation.get('differences'), list), 'VERIFICATION_INVALID')
        if validation['status'] == 'verified':
            require(not validation['differences'] and bool(validation.get('evidenceIds')), 'VERIFICATION_EVIDENCE_REQUIRED')
        op['verification'] = deepcopy(validation)
        op['status'] = {'verified': 'verified', 'mismatch': 'failed', 'incomplete': 'verification_pending'}[validation['status']]
    return _change(store, operation_id, change)


def next_actions(store):
    return [{'operationId': op['operationId'], 'status': op['status'],
             'nextAction': 'dispatch' if op['status'] == 'prepared' else 'reconcile',
             'kind': op['kind'], 'target': op['target']} for op in store.read()['operations'].values() if op['status'] != 'verified']
