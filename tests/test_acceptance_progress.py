import copy
import importlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'review-k1-function' / 'scripts'


def test_workflow_can_initialize_version_progress(monkeypatch, snapshot, tmp_path):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    from acceptance_workflow import execute
    result = execute('progress', 'init', snapshot, tmp_path / 'version-progress')
    assert result['counts'] == {'total': 5, 'completed': 0, 'pending': 3, 'running': 2, 'incomplete': 0}


@pytest.fixture
def api(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    return importlib.import_module('acceptance.progress')


@pytest.fixture
def snapshot():
    return {'schemaVersion': 1, 'versionDate': '2026-10-21', 'acceptanceMode': 'mainline_regression',
            'source': {'tableId': 'table-1', 'revision': 'v1', 'capturedAt': '2026-10-21T10:00:00+08:00', 'complete': True},
            'items': [{'id': name, 'title': '需求' + name, 'status': status} for name, status in
                      [('A', 'running'), ('B', 'pending'), ('C', 'pending'), ('D', 'pending'), ('E', 'running')]]}


@pytest.fixture
def store(api, snapshot, tmp_path):
    obj = api.ProgressStore(tmp_path / 'progress')
    obj.initialize(snapshot)
    return obj


def event(tmp_path, item='B', status='passed', revision=0, event_id='event-b', conclusion=None):
    evidence = tmp_path / (event_id + '.txt')
    evidence.write_text('已保存的需求级验收证据', encoding='utf-8')
    return {'eventId': event_id, 'itemId': item, 'expectedItemRevision': revision, 'status': status,
            'conclusion': conclusion or status, 'conclusionFinal': True, 'scopeComplete': True,
            'evidence': [str(evidence)]}


def test_counts_are_requirement_level_and_result_enqueue_is_atomic(store, tmp_path):
    first = store.record(event(tmp_path))
    second = store.record(event(tmp_path, 'C', 'failed', event_id='event-c'))
    assert first['counts'] == {'total': 5, 'completed': 1, 'pending': 2, 'running': 2, 'incomplete': 0}
    assert second['counts'] == {'total': 5, 'completed': 1, 'pending': 1, 'running': 2, 'incomplete': 1}
    data = store.read()
    assert data['items']['B']['status'] == 'passed'
    assert len(data['outbox']) == 2
    assert data['outbox'][0]['counts']['pending'] == 2
    assert data['outbox'][1]['counts']['incomplete'] == 1
    assert '进度播报' in data['outbox'][0]['payload']['markdown']['text']
    assert '版本日验收' in data['outbox'][0]['payload']['markdown']['text']
    assert '需求B' in data['outbox'][0]['payload']['markdown']['text']
    assert data['outbox'][0]['payload']['at']['isAtAll'] is False


def test_partial_case_progress_does_not_send_completion(store):
    store.record({'eventId': 'start-b', 'itemId': 'B', 'expectedItemRevision': 0, 'status': 'running'})
    assert store.status()['counts']['running'] == 3
    assert store.read()['outbox'] == []


def test_replayed_event_is_idempotent_and_conflicting_id_is_rejected(store, tmp_path):
    request = event(tmp_path)
    store.record(request)
    store.record(request)
    assert len(store.read()['outbox']) == 1
    with pytest.raises(ValueError, match='EVENT_ID_CONFLICT'):
        store.record({**request, 'status': 'failed'})


def test_same_conclusion_after_retest_is_quiet_but_changed_result_notifies(store, tmp_path):
    store.record(event(tmp_path, status='failed'))
    store.record({'eventId': 'retest', 'itemId': 'B', 'expectedItemRevision': 1, 'status': 'running'})
    store.record(event(tmp_path, status='failed', revision=2, event_id='repeat'))
    assert len(store.read()['outbox']) == 1
    store.record(event(tmp_path, status='passed', revision=3, event_id='fixed'))
    assert len(store.read()['outbox']) == 2
    assert store.status()['counts']['completed'] == 1


@pytest.mark.parametrize('change,code', [({'scopeComplete': False}, 'SCOPE_INCOMPLETE'),
                                        ({'conclusionFinal': False}, 'FINAL_CONCLUSION_REQUIRED'),
                                        ({'evidence': []}, 'EVIDENCE_REQUIRED'),
                                        ({'expectedItemRevision': 9}, 'ITEM_REVISION_CONFLICT')])
def test_unverified_or_stale_completion_cannot_change_counts(store, tmp_path, change, code):
    with pytest.raises(ValueError, match=code):
        store.record({**event(tmp_path), **change})
    assert store.status()['counts']['completed'] == 0
    assert not store.read()['outbox']


def test_full_snapshot_and_unique_requirement_ids_are_required(api, snapshot, tmp_path):
    snapshot['source']['complete'] = False
    with pytest.raises(ValueError, match='FULL_VERSION_SNAPSHOT_REQUIRED'):
        api.ProgressStore(tmp_path / 'bad').initialize(snapshot)
    snapshot['source']['complete'] = True
    snapshot['items'].append(copy.deepcopy(snapshot['items'][0]))
    with pytest.raises(ValueError, match='DUPLICATE_ITEM'):
        api.ProgressStore(tmp_path / 'bad').initialize(snapshot)


def test_concurrent_different_items_preserve_both_results(store, tmp_path):
    requests = [event(tmp_path), event(tmp_path, 'C', 'blocked', event_id='event-c')]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(store.record, requests))
    assert store.status()['counts'] == {'total': 5, 'completed': 1, 'pending': 1, 'running': 2, 'incomplete': 1}
    assert [x['sequence'] for x in store.read()['outbox']] == [1, 2]


def test_roster_refresh_cannot_reset_results_or_cross_modes(store, snapshot, tmp_path):
    store.record(event(tmp_path))
    with pytest.raises(ValueError, match='REVISION_CONFLICT'):
        store.sync({**snapshot, 'expectedRevision': 0})
    snapshot['items'][1]['status'] = 'passed'
    snapshot['items'].append({'id': 'F', 'title': '新需求', 'status': 'pending'})
    snapshot['source']['revision'] = 'v2'
    store.sync({**snapshot, 'expectedRevision': 1, 'reason': '进包表增加F'})
    assert store.status()['counts']['total'] == 6
    assert store.status()['counts']['completed'] == 1
    with pytest.raises(ValueError, match='SCOPE_MISMATCH'):
        store.sync({**snapshot, 'acceptanceMode': 'development', 'expectedRevision': 2})


def test_delivery_success_is_not_repeated(store, tmp_path):
    store.record(event(tmp_path))
    delivered = []
    def sender(payload):
        delivered.append(payload)
        return {'outcome': 'sent', 'code': 'OK'}
    store.flush(sender=sender, clock=lambda: 1000)
    store.flush(sender=sender, clock=lambda: 1001)
    assert len(delivered) == 1
    assert store.read()['outbox'][0]['delivery'] == 'sent'


def test_known_rejection_is_retried_later_without_blocking_acceptance(store, tmp_path):
    store.record(event(tmp_path))
    store.flush(sender=lambda _: {'outcome': 'retry', 'code': 'REJECTED'}, clock=lambda: 1000)
    assert store.read()['outbox'][0]['delivery'] == 'pending'
    store.record(event(tmp_path, 'C', 'failed', event_id='event-c'))
    sent = []
    store.flush(sender=lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'}, clock=lambda: 1001)
    assert len(sent) == 1  # C sends immediately; B has a scheduled retry.
    store.flush(sender=lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'}, clock=lambda: 2000)
    assert len(sent) == 2
    assert store.status()['counts']['incomplete'] == 1


def test_timeout_is_unknown_and_requires_evidence_before_resend(store, tmp_path):
    store.record(event(tmp_path))
    def timeout(_):
        raise TimeoutError('private webhook must never be logged')
    store.flush(sender=timeout, clock=lambda: 1000)
    calls = []
    store.flush(sender=lambda p: calls.append(p), clock=lambda: 2000)
    assert calls == []
    assert store.read()['outbox'][0]['delivery'] == 'unknown'
    assert 'private webhook' not in json.dumps(store.read())
    with pytest.raises(ValueError, match='RECONCILIATION_EVIDENCE_REQUIRED'):
        store.resolve({'sequence': 1, 'outcome': 'not_sent', 'evidence': []})
    proof = tmp_path / 'group-readback.txt'
    proof.write_text('群回读确认该事件未发送', encoding='utf-8')
    store.resolve({'sequence': 1, 'outcome': 'not_sent', 'evidence': [str(proof)]})
    store.flush(sender=lambda _: {'outcome': 'sent', 'code': 'OK'}, clock=lambda: 3000)
    assert store.read()['outbox'][0]['delivery'] == 'sent'


def test_crash_after_dispatch_does_not_resend_on_restart(store, tmp_path):
    store.record(event(tmp_path))
    def crash(_):
        raise SystemExit('process stopped after sending')
    with pytest.raises(SystemExit):
        store.flush(sender=crash, clock=lambda: 1000)
    store.flush(sender=lambda _: pytest.fail('must not resend an in-flight message'), clock=lambda: 2000)
    assert store.read()['outbox'][0]['delivery'] == 'unknown'


def test_cli_persists_result_even_when_private_config_missing(store, tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    cli = importlib.import_module('acceptance_progress')
    result = cli.execute('record', event(tmp_path), store.root, tmp_path / 'missing.private.json')
    assert result['counts']['completed'] == 1
    assert result['notification']['error'] == 'ROBOT_CONFIG_UNAVAILABLE'
    assert store.read()['outbox'][0]['delivery'] == 'pending'


def test_retries_stop_after_three_confirmed_failures(store, tmp_path):
    store.record(event(tmp_path))
    sent = []
    for when in (1000, 2000, 3000, 4000):
        store.flush(sender=lambda p: sent.append(p) or {'outcome': 'retry', 'code': 'API_310000'}, clock=lambda: when)
    assert len(sent) == 3
    assert store.read()['outbox'][0]['delivery'] == 'failed'


def test_concurrent_senders_cannot_deliver_same_message_twice(store, tmp_path):
    import threading
    store.record(event(tmp_path))
    entered, release = threading.Event(), threading.Event()
    calls = []
    def slow_sender(payload):
        calls.append(payload)
        entered.set()
        assert release.wait(5)
        return {'outcome': 'sent', 'code': 'OK'}
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(store.flush, slow_sender)
        assert entered.wait(5)
        try:
            with pytest.raises(ValueError, match='PROGRESS_BUSY'):
                store.flush(sender=lambda _: pytest.fail('second sender must not execute'))
            # Saving a different requirement is independent of network delivery.
            store.record(event(tmp_path, 'C', 'failed', event_id='concurrent-c'))
        finally:
            release.set()
        future.result()
    assert len(calls) == 2
    assert all(e['delivery'] == 'sent' for e in store.read()['outbox'])


def test_membership_sync_never_overwrites_existing_result(store, snapshot, tmp_path):
    store.record(event(tmp_path))
    with pytest.raises(ValueError, match='SYNC_CANNOT_CHANGE_RESULTS'):
        store.sync({**snapshot, 'expectedRevision': 1})
    assert store.status()['counts']['completed'] == 1


def test_unknown_delivery_does_not_stop_later_conclusions(store, tmp_path):
    store.record(event(tmp_path))
    store.flush(sender=lambda _: {'outcome': 'unknown', 'code': 'TIMEOUT'}, clock=lambda: 1000)
    store.record(event(tmp_path, 'C', 'blocked', event_id='c-blocked'))
    store.flush(sender=lambda _: {'outcome': 'sent', 'code': 'OK'}, clock=lambda: 2000)
    assert [x['delivery'] for x in store.read()['outbox']] == ['unknown', 'sent']


def test_cli_record_auto_sends_and_rerun_keeps_one_message(store, tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    cli = importlib.import_module('acceptance_progress')
    sent = []
    monkeypatch.setattr(cli, 'RobotClient', lambda _: lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'})
    request = event(tmp_path)
    cli.execute('record', request, store.root)
    cli.execute('record', request, store.root)
    assert len(sent) == 1
    assert store.read()['outbox'][0]['delivery'] == 'sent'


def test_provider_retry_delay_is_preserved(store, tmp_path):
    store.record(event(tmp_path))
    store.flush(sender=lambda _: {'outcome': 'retry', 'code': 'HTTP_429', 'retryAfterSeconds': 600}, clock=lambda: 1000)
    store.flush(sender=lambda _: pytest.fail('provider retry window has not elapsed'), clock=lambda: 1500)
    assert store.read()['outbox'][0]['nextAttemptAt'] == 1600
