import importlib
from pathlib import Path

import pytest


@pytest.fixture
def owners(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'review-k1-function/scripts'))
    return importlib.import_module('acceptance.owners')


def member(name, open_id):
    return {'memberEmpName': name, 'memberNick': name, 'openDingtalkId': open_id}


def candidate(name, user_id, open_id):
    return {'title': name, 'userId': user_id, 'openDingTalkId': open_id}


def directory(members, people):
    def call(args):
        if args[:3] == ['chat', 'group', 'members']:
            return {'success': True, 'result': {'list': members, 'hasMore': False}}
        return {'success': True, 'result': people.get(args[3], [])}
    return call


def test_owner_names_are_split_and_deduplicated_without_losing_inactive_markers(owners):
    assert owners.owner_names('甲、乙，甲;丙 [X]\n丁') == ['甲', '乙', '丙 [X]', '丁']


def test_resolves_exact_directory_identity_in_the_group(owners):
    resolver = owners.OwnerResolver({'groupName': '播报群', 'openConversationId': 'group-test'},
                                    runner=directory([member('甲', 'open-a'), member('乙', 'open-b')],
                                                     {'甲': [candidate('甲', 'user-a', 'open-a')],
                                                      '乙': [candidate('乙', 'user-b', 'open-b')]}))
    result = resolver.resolve('甲、乙、甲')
    assert result['userIds'] == ['user-a', 'user-b']
    assert result['unresolved'] == []


def test_group_nickname_does_not_prevent_matching_verified_directory_identity(owners):
    resolver = owners.OwnerResolver({'groupName': '群', 'openConversationId': 'g'},
                                    runner=directory([{'memberNick': '花名', 'openDingtalkId': 'open-a'}],
                                                     {'甲': [candidate('甲', 'user-a', 'open-a')]}))
    assert resolver.resolve('甲')['userIds'] == ['user-a']


def test_aliases_for_the_same_member_only_mention_one_user_id(owners):
    resolver = owners.OwnerResolver({'groupName': '群', 'openConversationId': 'g'},
                                    runner=directory([member('甲', 'open-a')],
                                                     {'甲': [candidate('甲', 'user-a', 'open-a')],
                                                      '甲别名': [candidate('甲别名', 'user-a', 'open-a')]}))
    assert resolver.resolve('甲、甲别名')['userIds'] == ['user-a']


def test_unknown_ambiguous_and_inactive_owners_are_not_guessed(owners):
    resolver = owners.OwnerResolver({'groupName': '群', 'openConversationId': 'g'},
                                    runner=directory([member('重名', 'open-a'), member('重名', 'open-b')],
                                                     {'重名': [candidate('重名', 'u-a', 'open-a'),
                                                               candidate('重名', 'u-b', 'open-b')],
                                                      '外部': [candidate('外部', 'u-c', 'open-c')]}))
    result = resolver.resolve(['重名', '外部', '旧人 [X]'])
    assert result['userIds'] == []
    assert [x['code'] for x in result['unresolved']] == ['OWNER_AMBIGUOUS', 'OWNER_NOT_IN_GROUP', 'OWNER_INACTIVE']


def test_lookup_failure_preserves_a_clear_unmentioned_warning(owners):
    def fail(_):
        raise OSError('private credential error must not escape')
    result = owners.OwnerResolver({'groupName': '群'}, runner=fail).resolve('甲')
    assert result['userIds'] == []
    assert result['unresolved'][0]['code'] == 'OWNER_LOOKUP_UNAVAILABLE'
    assert 'private' not in str(result)


def test_group_search_and_members_are_fully_paginated(owners):
    calls = []
    def call(args):
        calls.append(args)
        if args[:2] == ['chat', 'search']:
            second = args[args.index('--cursor') + 1] == 'second'
            return {'success': True, 'result': {'value': [{'title': '群', 'openConversationId': 'g'}] if second else [],
                                                'hasMore': not second, 'nextCursor': 'second'}}
        if args[:3] == ['chat', 'group', 'members']:
            second = args[args.index('--cursor') + 1] == 'second'
            return {'success': True, 'result': {'list': [member('甲', 'open-a')] if second else [],
                                                'hasMore': not second, 'nextCursor': 'second'}}
        return {'success': True, 'result': [candidate('甲', 'user-a', 'open-a')]}
    assert owners.OwnerResolver({'groupName': '群'}, runner=call).resolve('甲')['userIds'] == ['user-a']
    assert len(calls) == 5


def test_native_dws_group_search_groups_field_is_supported(owners):
    def call(args):
        if args[:2] == ['chat', 'search']:
            return {'success': True, 'result': {'groups': [{'title': '群', 'openConversationId': 'g'}],
                                                'hasMore': False}}
        return directory([member('甲', 'open-a')], {'甲': [candidate('甲', 'user-a', 'open-a')]})(args)
    assert owners.OwnerResolver({'groupName': '群'}, runner=call).resolve('甲')['userIds'] == ['user-a']


def test_apply_mentions_uses_user_ids_and_never_at_all(owners):
    original = {'msgtype': 'markdown', 'markdown': {'title': '进度播报｜验收未通过',
                 'text': '进度播报\n\n**问题**：失败'}, 'at': {'isAtAll': False}}
    result = owners.apply_mentions(original, {'userIds': ['user-a', 'user-a'], 'unresolved': []})
    assert result['at'] == {'atUserIds': ['user-a'], 'isAtAll': False}
    assert '@user-a' in result['markdown']['text']
    assert original['at'] == {'isAtAll': False}


@pytest.fixture
def store(owners, tmp_path):
    from acceptance.progress import ProgressStore
    obj = ProgressStore(tmp_path / 'ledger')
    obj.initialize({'schemaVersion': 1, 'versionDate': '2026-11-06', 'acceptanceMode': 'mainline_regression',
                    'source': {'tableId': 'test', 'revision': 'v1', 'capturedAt': '2026-11-06T10:00:00+08:00', 'complete': True},
                    'items': [{'id': 'A', 'title': '需求A', 'status': 'pending', 'owners': ['甲']},
                              {'id': 'B', 'title': '需求B', 'status': 'pending'}]})
    return obj


def record(store, tmp_path, item='A', status='failed', **extra):
    proof = tmp_path / 'proof.txt'
    proof.write_text('实际验收证据与在线回读', encoding='utf-8')
    return store.record({'eventId': item, 'itemId': item, 'expectedItemRevision': 0, 'status': status,
                         'conclusion': '真实结论', 'conclusionFinal': True, 'scopeComplete': True,
                         'evidence': [str(proof)], **extra})


def test_mentions_are_prepared_outside_ledger_lock_and_frozen_on_retry(store, tmp_path):
    record(store, tmp_path)
    prepared, sent = [], []
    class Sender:
        def prepare_failure(self, names):
            prepared.append(names)
            store.record({'eventId': 'b-start', 'itemId': 'B', 'expectedItemRevision': 0, 'status': 'running'})
            return {'userIds': ['user-a'], 'unresolved': []}
        def __call__(self, payload):
            sent.append(payload)
            return {'outcome': 'retry' if len(sent) == 1 else 'sent', 'code': 'TEST'}
    sender = Sender()
    store.flush(sender, clock=lambda: 1000)
    store.flush(sender, clock=lambda: 2000)
    assert prepared == [['甲']]
    assert sent[0] == sent[1]
    assert sent[0]['at']['atUserIds'] == ['user-a']


def test_round_summary_never_resolves_or_mentions_owners(store, tmp_path):
    record(store, tmp_path, 'A', 'passed')
    record(store, tmp_path, 'B', 'passed')
    proof = tmp_path / 'proof.txt'
    store.summarize({'roundId': 'r', 'expectedRevision': store.status()['revision'], 'roundComplete': True,
                     'itemIds': ['A', 'B'], 'evidence': [str(proof)]})
    class Sender:
        def prepare_failure(self, _):
            pytest.fail('summary must not resolve people')
        def __call__(self, payload):
            assert payload['at'] == {'isAtAll': False}
            assert '@user-' not in payload['markdown']['text']
            return {'outcome': 'sent', 'code': 'OK'}
    store.flush(Sender())


def test_sync_refreshes_owner_names_and_explicit_empty_clears_them(store):
    snapshot = {**store.read(), 'items': [{'id': 'A', 'title': '需求A', 'status': 'pending', 'owners': ['乙']},
                                        {'id': 'B', 'title': '需求B', 'status': 'pending'}], 'expectedRevision': 0}
    store.sync(snapshot)
    assert store.read()['items']['A']['owners'] == ['乙']
    snapshot['expectedRevision'] = 1
    snapshot['items'][0]['owners'] = []
    store.sync(snapshot)
    assert store.read()['items']['A']['owners'] == []


def test_missing_owner_still_sends_failure_with_an_explicit_warning(store, tmp_path):
    record(store, tmp_path, owners=[])
    class Sender:
        def prepare_failure(self, names):
            from acceptance.owners import OwnerResolver
            return OwnerResolver({'groupName': '群'}, runner=lambda _: pytest.fail('no owner needs no query')).resolve(names)
        def __call__(self, payload):
            assert payload['at'] == {'isAtAll': False}
            assert '未能定向提醒' in payload['markdown']['text']
            assert '未填写' in payload['markdown']['text']
            return {'outcome': 'sent', 'code': 'OK'}
    store.flush(Sender())
    assert store.status()['notifications'][0]['mentionResolution']['unresolved'][0]['code'] == 'OWNER_MISSING'


def test_unknown_receipt_never_reresolves_or_resends(store, tmp_path):
    record(store, tmp_path)
    class Sender:
        queries = 0
        sends = 0
        def prepare_failure(self, names):
            self.queries += 1
            return {'userIds': ['user-a'], 'unresolved': []}
        def __call__(self, payload):
            self.sends += 1
            return {'outcome': 'unknown', 'code': 'TIMEOUT'}
    sender = Sender()
    store.flush(sender)
    store.flush(sender)
    assert (sender.queries, sender.sends) == (1, 1)


def test_legacy_pending_message_keeps_its_original_unmentioned_payload(store, tmp_path):
    from acceptance.core import atomic_json
    record(store, tmp_path)
    data = store.read()
    data['outbox'][0].pop('mentionPolicy')
    original = data['outbox'][0]['payload']
    atomic_json(store.path, data)
    class Sender:
        def prepare_failure(self, _):
            pytest.fail('do not add mentions retroactively')
        def __call__(self, payload):
            assert payload == original
            return {'outcome': 'sent', 'code': 'OK'}
    store.flush(Sender())
