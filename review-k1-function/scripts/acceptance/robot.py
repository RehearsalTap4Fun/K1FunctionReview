"""DingTalk custom webhook transport. Never return credentials or raw errors."""
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import math
import os
from pathlib import Path
import socket
import urllib.error
import urllib.parse
import urllib.request

from .core import WorkflowError, read_json, require


def default_config():
    return Path(os.environ.get('K1_PROGRESS_ROBOT_CONFIG') or
                Path.home() / '.codex/private/review-k1-function/progress-robot.local.json')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def retry_after(value):
    try:
        seconds = int(value)
        return seconds if seconds >= 0 else 60
    except (ValueError, TypeError):
        try:
            target = parsedate_to_datetime(value)
            return max(0, math.ceil((target - datetime.now(timezone.utc)).total_seconds()))
        except (ValueError, TypeError, OverflowError):
            return 60


class RobotClient:
    def __init__(self, config_path=None):
        try:
            self.config = read_json(config_path or default_config())
        except (OSError, ValueError, UnicodeError):
            raise WorkflowError('ROBOT_CONFIG_UNAVAILABLE') from None
        require(isinstance(self.config, dict) and self.config.get('schemaVersion') == 1, 'ROBOT_CONFIG_INVALID')
        require(self.config.get('keyword') == '进度播报' and self.config.get('groupName'), 'ROBOT_CONFIG_INVALID')
        try:
            parsed = urllib.parse.urlsplit(self.config.get('webhook', ''))
            query = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
            valid = (parsed.scheme == 'https' and parsed.netloc == 'oapi.dingtalk.com'
                     and parsed.path == '/robot/send' and not parsed.fragment
                     and set(query) == {'access_token'} and len(query['access_token']) == 1
                     and bool(query['access_token'][0]))
        except (ValueError, TypeError):
            valid = False
        require(valid, 'ROBOT_WEBHOOK_INVALID')
        self.opener = urllib.request.build_opener(NoRedirect())

    def check(self):
        return {'configured': True, 'groupName': self.config['groupName'], 'keyword': self.config['keyword']}

    def __call__(self, payload):
        require('进度播报' in payload['markdown']['text'] and payload['at'] == {'isAtAll': False}, 'ROBOT_MESSAGE_INVALID')
        request = urllib.request.Request(self.config['webhook'],
                                         data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                                         headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
        try:
            with self.opener.open(request, timeout=5) as response:
                raw = response.read(65537)
                if len(raw) > 65536:
                    return {'outcome': 'unknown', 'code': 'RESPONSE_TOO_LARGE'}
                result = json.loads(raw)
            if not isinstance(result, dict) or type(result.get('errcode')) is not int:
                return {'outcome': 'unknown', 'code': 'INVALID_RESPONSE'}
            return {'outcome': 'sent' if result['errcode'] == 0 else 'retry', 'code': 'API_' + str(result['errcode'])}
        except urllib.error.HTTPError as error:
            result = {'outcome': 'retry' if 400 <= error.code < 500 and error.code != 408 else 'unknown',
                      'code': 'HTTP_' + str(error.code)}
            if error.code == 429:
                result['retryAfterSeconds'] = retry_after(error.headers.get('Retry-After'))
            return result
        except urllib.error.URLError as error:
            definite = isinstance(error.reason, (socket.gaierror, ConnectionRefusedError))
            return {'outcome': 'retry' if definite else 'unknown', 'code': 'CONNECT_FAILED' if definite else 'DELIVERY_UNKNOWN'}
        except (OSError, ValueError, UnicodeError):
            return {'outcome': 'unknown', 'code': 'DELIVERY_UNKNOWN'}
