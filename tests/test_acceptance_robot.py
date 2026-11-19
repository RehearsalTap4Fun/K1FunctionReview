import importlib
import io
import json
from pathlib import Path
import socket
import subprocess
import urllib.error

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'review-k1-function' / 'scripts'


@pytest.fixture
def robot(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    module = importlib.import_module('acceptance.robot')
    config = tmp_path / 'robot.private.json'
    config.write_text(json.dumps({'schemaVersion': 1, 'keyword': '进度播报', 'groupName': '测试群',
                                 'webhook': 'https://oapi.dingtalk.com/robot/send?access_token=TEST_ONLY_NOT_A_CREDENTIAL'}), encoding='utf-8')
    return module, config


def payload():
    return {'msgtype': 'markdown', 'markdown': {'title': '进度播报', 'text': '进度播报｜测试'}, 'at': {'isAtAll': False}}


@pytest.mark.parametrize('response,want', [(b'{"errcode":0,"errmsg":"ok"}', 'accepted'),
                                           (b'{"errcode":310000,"errmsg":"secret must not escape"}', 'retry'),
                                           (b'{"errcode":false}', 'unknown'),
                                           (b'{}', 'unknown'), (b'not json', 'unknown')])
def test_provider_receipt_requires_explicit_success(robot, response, want):
    module, config = robot
    client = module.RobotClient(config)
    class Transport:
        def open(self, request, timeout):
            assert request.get_method() == 'POST'
            assert request.get_header('Content-type') == 'application/json; charset=utf-8'
            assert json.loads(request.data) == payload()
            assert timeout <= 10
            return io.BytesIO(response)
    client.opener = Transport()
    result = client(payload())
    assert result['outcome'] == want
    assert 'secret' not in json.dumps(result)


def test_group_readback_matches_exact_broadcast_id_in_configured_group(robot):
    module, config = robot
    client = module.RobotClient(config)
    client.config['openConversationId'] = 'cid-test'
    calls = []

    def read(args):
        calls.append(args)
        assert args[:5] == ['chat', 'message', 'list', '--group', 'cid-test']
        return {'success': True, 'result': {'messages': [
            {'text': '播报编号：0123456789ab\\-10', 'openMessageId': 'wrong-number'},
            {'text': '播报编号：0123456789ab\\-1', 'openMessageId': 'wrong-group',
             'openConversationId': 'different-group'},
            {'text': '### 验收未通过\n播报编号：0123456789ab\\-1', 'openMessageId': 'right-message',
             'openConversationId': 'cid-test', 'createTime': '2026-11-19 10:40:01'},
        ]}}

    client.owner_resolver.runner = read
    message = payload()
    message['markdown']['text'] += '\n播报编号：0123456789ab\\-1'
    receipt = client.confirm_delivery(message, 1795056000)
    assert receipt == {'messageId': 'right-message', 'createdAt': '2026-11-19 10:40:01'}
    assert len(calls) == 1


def test_group_readback_checks_later_pages(robot, monkeypatch):
    module, config = robot
    client = module.RobotClient(config)
    client.config['openConversationId'] = 'cid-test'

    def run(command, **kwargs):
        assert '--page-all' in command
        assert command[command.index('--direction') + 1] == 'newer'
        response = {'complete': True, 'hasMore': False, 'pagesFetched': 2, 'messages': [
            {'text': '播报编号：0123456789ab-1', 'messageId': 'second-page-message',
             'createTime': '2026-11-19 10:40:01'},
        ]}
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(response))

    monkeypatch.setattr('acceptance.owners.subprocess.run', run)
    message = payload()
    message['markdown']['text'] += '\n播报编号：0123456789ab-1'
    assert client.confirm_delivery(message, 1795056000)['messageId'] == 'second-page-message'


@pytest.mark.parametrize('error,want', [(TimeoutError('private token'), 'unknown'),
                                       (urllib.error.URLError(socket.gaierror('private token')), 'retry'),
                                       (urllib.error.URLError(ConnectionRefusedError('private token')), 'retry'),
                                       (urllib.error.URLError(ConnectionResetError('private token')), 'unknown'),
                                       (urllib.error.HTTPError('private token', 408, 'timeout', {}, None), 'unknown'),
                                       (urllib.error.HTTPError('private token', 429, 'limited', {}, None), 'retry'),
                                       (urllib.error.HTTPError('private token', 502, 'upstream', {}, None), 'unknown')],
                         ids=['timeout', 'dns', 'refused', 'reset', 'http-timeout', 'rate-limited', 'upstream'])
def test_network_failures_distinguish_safe_retry_from_ambiguous_delivery(robot, error, want):
    module, config = robot
    client = module.RobotClient(config)
    class Transport:
        def open(self, request, timeout):
            raise error
    client.opener = Transport()
    result = client(payload())
    assert result['outcome'] == want
    assert 'private' not in json.dumps(result)


@pytest.mark.parametrize('url', ['http://oapi.dingtalk.com/robot/send?access_token=x',
                                  'https://example.invalid/robot/send?access_token=x',
                                  'https://oapi.dingtalk.com/robot/send?access_token=x&access_token=y',
                                  'https://oapi.dingtalk.com/robot/send?access_token=x#fragment'])
def test_webhook_validation_prevents_wrong_destination(robot, url):
    module, config = robot
    data = json.loads(config.read_text(encoding='utf-8')); data['webhook'] = url
    config.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(ValueError, match='ROBOT_WEBHOOK_INVALID'):
        module.RobotClient(config)


def test_configuration_check_never_returns_token(robot):
    module, config = robot
    check = module.RobotClient(config).check()
    assert check == {'configured': True, 'groupName': '测试群', 'keyword': '进度播报'}
    assert 'TEST_ONLY' not in json.dumps(check)


def test_transport_accepts_scoped_user_id_mentions(robot):
    module, config = robot
    client = module.RobotClient(config)
    data = payload()
    data['at']['atUserIds'] = ['user-a']
    data['markdown']['text'] += '\n\n@user-a'
    class Transport:
        def open(self, request, timeout):
            assert json.loads(request.data)['at'] == {'atUserIds': ['user-a'], 'isAtAll': False}
            return io.BytesIO(b'{"errcode":0,"errmsg":"ok"}')
    client.opener = Transport()
    assert client(data)['outcome'] == 'accepted'


@pytest.mark.parametrize('at', [{'isAtAll': True}, {'isAtAll': False, 'atMobiles': ['not-allowed']},
                                {'isAtAll': False, 'atUserIds': ['bad\n@all']}])
def test_transport_forbids_at_all_phones_and_invalid_user_ids(robot, at):
    module, config = robot
    data = payload()
    data['at'] = at
    with pytest.raises(ValueError, match='ROBOT_MESSAGE_INVALID'):
        module.RobotClient(config)(data)


def test_transport_rejects_mentions_on_round_summary(robot):
    module, config = robot
    data = payload()
    data['markdown']['title'] = '进度播报｜整轮验收汇总'
    data['at']['atUserIds'] = ['user-a']
    with pytest.raises(ValueError, match='SUMMARY_MUST_NOT_MENTION'):
        module.RobotClient(config)(data)


def test_redirect_is_not_followed_with_credentials(robot):
    module, _ = robot
    assert module.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.invalid') is None


def test_rate_limit_honors_provider_retry_after(robot):
    module, config = robot
    client = module.RobotClient(config)
    class Transport:
        def open(self, request, timeout):
            raise urllib.error.HTTPError('private token', 429, 'limited', {'Retry-After': '600'}, None)
    client.opener = Transport()
    assert client(payload()) == {'outcome': 'retry', 'code': 'HTTP_429', 'retryAfterSeconds': 600}


@pytest.mark.parametrize('value,want', [('-1', 60), ('invalid', 60), (None, 60), ('0', 0), ('90', 90)])
def test_invalid_retry_after_does_not_remove_rate_limit_wait(robot, value, want):
    module, _ = robot
    assert module.retry_after(value) == want
