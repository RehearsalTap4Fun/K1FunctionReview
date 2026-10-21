import importlib
import io
import json
from pathlib import Path
import socket
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


@pytest.mark.parametrize('response,want', [(b'{"errcode":0,"errmsg":"ok"}', 'sent'),
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
