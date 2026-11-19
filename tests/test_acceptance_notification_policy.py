"""Failure-only delivery and round summaries, using an in-memory sender."""
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def store(tmp_path, monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / 'review-k1-function' / 'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    obj = importlib.import_module('acceptance.progress').ProgressStore(tmp_path / 'ledger')
    obj.initialize({'schemaVersion': 1, 'versionDate': '2026-11-06',
                    'acceptanceMode': 'mainline_regression',
                    'source': {'tableId': 'test', 'revision': 'v1',
                               'capturedAt': '2026-11-06T10:00:00+08:00', 'complete': True},
                    'items': [{'id': key, 'title': key, 'status': 'pending'} for key in 'ABC']})
    return obj


def result(store, tmp_path, key, status, revision=0, event_id=None):
    proof = tmp_path / 'evidence.txt'
    proof.write_text('需求级证据与在线回读', encoding='utf-8')
    return store.record({'eventId': event_id or key, 'itemId': key, 'status': status,
                         'expectedItemRevision': revision, 'conclusionFinal': True,
                         'scopeComplete': True, 'conclusion': '结果：' + status,
                         'evidence': [str(proof)]})


def summary_request(store, tmp_path):
    proof = tmp_path / 'summary.txt'
    proof.write_text('本轮全部需求已处理，报告及在线回读已核对', encoding='utf-8')
    return {'roundId': 'round-1', 'expectedRevision': store.status()['revision'],
            'roundComplete': True, 'itemIds': list('ABC'), 'evidence': [str(proof)]}


def test_only_failed_results_enqueue(store, tmp_path):
    for key, status in zip('ABC', ['passed', 'failed', 'blocked']):
        result(store, tmp_path, key, status)
    messages = store.read()['outbox']
    assert [m['itemId'] for m in messages] == ['B']
    assert store.status()['counts'] == {'total': 3, 'completed': 1, 'pending': 0,
                                        'running': 0, 'incomplete': 2}


def test_fixed_then_failed_again_notifies_again(store, tmp_path):
    result(store, tmp_path, 'A', 'failed')
    result(store, tmp_path, 'A', 'passed', 1, 'fixed')
    result(store, tmp_path, 'A', 'failed', 2, 'regressed')
    assert len(store.read()['outbox']) == 2


def test_round_summary_is_durable_and_idempotent(store, tmp_path):
    for key, status in zip('ABC', ['passed', 'failed', 'blocked']):
        result(store, tmp_path, key, status)
    request = summary_request(store, tmp_path)
    store.summarize(request)
    store.summarize(request)
    sent = []
    sender = lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'}
    store.flush(sender)
    store.flush(sender)
    assert len(sent) == 2
    assert '整轮验收汇总' in sent[1]['markdown']['text']
    assert '未通过：1' in sent[1]['markdown']['text']
    assert '阻塞：1' in sent[1]['markdown']['text']
    assert len(store.read()['roundSummaries']) == 1


def test_unfinished_round_cannot_summarize(store, tmp_path):
    result(store, tmp_path, 'A', 'passed')
    with pytest.raises(ValueError, match='ROUND_NOT_FINISHED'):
        store.summarize(summary_request(store, tmp_path))


def test_summary_can_close_only_the_current_round_scope(store, tmp_path):
    result(store, tmp_path, 'A', 'passed')
    request = {**summary_request(store, tmp_path), 'itemIds': ['A']}
    store.summarize(request)
    assert store.read()['outbox'][0]['counts']['total'] == 1
    with pytest.raises(ValueError, match='ROUND_ID_CONFLICT'):
        store.summarize({**request, 'itemIds': ['A', 'B']})


def test_legacy_outbox_does_not_send_passed_or_blocked(store, tmp_path):
    from acceptance.core import atomic_json
    for key, status in zip('ABC', ['passed', 'failed', 'blocked']):
        result(store, tmp_path, key, status)
    data = store.read()
    # Simulate pending entries produced by the old all-results implementation.
    for key in ['A', 'C']:
        data['outbox'].append({'sequence': len(data['outbox']) + 1, 'itemId': key,
                               'eventId': key, 'delivery': 'pending', 'attempts': 0,
                               'nextAttemptAt': 0, 'payload': {}})
    atomic_json(store.path, data)
    sent = []
    store.flush(lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'})
    assert len(sent) == 1
    assert [m['delivery'] for m in store.read()['outbox']] == ['sent', 'suppressed', 'suppressed']


def test_cli_round_summary_uses_the_same_durable_sender(store, tmp_path, monkeypatch):
    cli = importlib.import_module('acceptance_progress')
    for key in 'ABC':
        result(store, tmp_path, key, 'passed')
    sent = []
    monkeypatch.setattr(cli, 'RobotClient', lambda _: lambda p: sent.append(p) or {'outcome': 'sent', 'code': 'OK'})
    request = summary_request(store, tmp_path)
    cli.execute('summarize', request, store.root)
    cli.execute('summarize', request, store.root)
    assert len(sent) == 1


def test_old_failure_is_not_sent_after_it_was_fixed(store, tmp_path):
    result(store, tmp_path, 'A', 'failed')
    result(store, tmp_path, 'A', 'passed', 1, 'fixed')
    store.flush(lambda _: pytest.fail('obsolete failure must not be broadcast'))
    assert store.read()['outbox'][0]['delivery'] == 'suppressed'
    assert store.read()['outbox'][0]['code'] == 'SUPERSEDED_RESULT'


def test_unknown_success_receipt_is_preserved(store, tmp_path):
    from acceptance.core import atomic_json
    result(store, tmp_path, 'A', 'passed')
    data = store.read()
    data['outbox'] = [{'sequence': 1, 'eventId': 'A', 'itemId': 'A', 'delivery': 'unknown',
                       'attempts': 1, 'nextAttemptAt': 0, 'payload': {}}]
    atomic_json(store.path, data)
    store.flush(lambda _: pytest.fail('unknown delivery must be reconciled first'))
    assert store.read()['outbox'][0]['delivery'] == 'unknown'


@pytest.mark.parametrize('change,code', [({'expectedRevision': -1}, 'REVISION_CONFLICT'),
                                       ({'roundComplete': False}, 'ROUND_NOT_FINISHED'),
                                       ({'evidence': []}, 'EVIDENCE_REQUIRED'),
                                       ({'itemIds': ['A', 'A']}, 'ROUND_ITEMS_REQUIRED')])
def test_invalid_summary_cannot_enqueue(store, tmp_path, change, code):
    for key in 'ABC':
        result(store, tmp_path, key, 'passed')
    with pytest.raises(ValueError, match=code):
        store.summarize({**summary_request(store, tmp_path), **change})
    assert store.read()['outbox'] == []


def test_display_metadata_is_persisted_and_used_by_round_summary(store, tmp_path):
    proof = tmp_path / 'actual-result.txt'
    proof.write_text('报告与在线表回读', encoding='utf-8')
    request = {'eventId': 'a-failed', 'itemId': 'A', 'expectedItemRevision': 0,
               'status': 'failed', 'conclusionFinal': True, 'conclusion': '阵容丢失',
               'evidence': [str(proof)],
               'display': {'issue': '重开后阵容丢失', 'expected': '保存阵容',
                           'environment': 'Unity · 2650', 'screenshots': [
                               {'url': 'https://images.example.test/real.png', 'caption': '失败现场'}]}}
    store.record(request)
    original = store.read()['outbox'][0]['payload']
    assert 'real.png' in original['markdown']['text']
    assert store.read()['items']['A']['display']['expected'] == '保存阵容'
    # Replacing evidence presentation does not create a new business failure.
    store.record({**request, 'eventId': 'a-new-image', 'expectedItemRevision': 1,
                  'display': {**request['display'], 'screenshots': []}})
    assert len(store.read()['outbox']) == 1
    assert store.read()['outbox'][0]['payload'] == original
    result(store, tmp_path, 'B', 'passed')
    result(store, tmp_path, 'C', 'blocked')
    store.summarize(summary_request(store, tmp_path))
    assert '重开后阵容丢失' in store.read()['outbox'][1]['payload']['markdown']['text']


def test_failure_reason_comes_before_heading_and_mentions_without_truncation(store, tmp_path):
    from acceptance.owners import apply_mentions

    proof = tmp_path / 'failure.txt'
    proof.write_text('服务器回执', encoding='utf-8')
    reason = '服务端在白银已解锁时仍允许更换主题。' + '复现边界条件。' * 90 + '重新拉取后主题仍然改变。'
    store.record({'eventId': 'failure', 'itemId': 'A', 'status': 'failed',
                  'expectedItemRevision': 0, 'conclusionFinal': True,
                  'conclusion': '测试步骤和已通过的用例。' * 30 + '失败原因：' + reason,
                  'evidence': [str(proof)]})
    entry = store.read()['outbox'][0]
    body = apply_mentions(entry['payload'], {'userIds': ['handler']})['markdown']['text']
    assert body.split('\n\n')[0] == '**失败原因**：' + reason
    assert body.index('@handler') > body.index('重新拉取后主题仍然改变。')


def test_structured_failure_reason_overrides_long_conclusion(store, tmp_path):
    proof = tmp_path / 'failure.txt'
    proof.write_text('服务器回执', encoding='utf-8')
    reason = '预期禁止切换，实际返回成功。' + '补充失败细节。' * 100 + '原因结束。'
    store.record({'eventId': 'failure', 'itemId': 'A', 'status': 'failed',
                  'expectedItemRevision': 0, 'conclusionFinal': True,
                  'conclusion': '环境前置和已通过的用例。' * 60,
                  'display': {'issue': reason}, 'evidence': [str(proof)]})
    assert store.read()['outbox'][0]['payload']['markdown']['text'].split('\n\n')[0] == '**失败原因**：' + reason


def test_ack_without_group_message_stays_unknown_and_resume_only_reads(store, tmp_path):
    result(store, tmp_path, 'A', 'failed')

    class Sender:
        calls = 0
        proof = None

        def __call__(self, payload):
            self.calls += 1
            return {'outcome': 'accepted', 'code': 'API_0'}

        def confirm_delivery(self, payload, attempted_at):
            assert attempted_at == 1800000000
            return self.proof

    sender = Sender()
    store.flush(sender, clock=lambda: 1800000000)
    first = store.status()['notifications'][0]
    assert first['delivery'] == 'unknown' and first['code'] == 'GROUP_READBACK_PENDING'
    assert sender.calls == 1

    sender.proof = {'messageId': 'msg-1', 'createdAt': '2027-01-15 16:00:01'}
    store.flush(sender, clock=lambda: 1800000030)
    delivered = store.status()['notifications'][0]
    assert delivered['delivery'] == 'sent'
    assert delivered['groupConfirmation']['messageId'] == 'msg-1'
    assert sender.calls == 1
