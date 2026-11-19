"""DingTalk custom webhook transport. Never return credentials or raw errors."""
import json
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import math
import os
from pathlib import Path
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

from .core import WorkflowError, read_json, require
from .owners import OwnerResolver, USER_ID


BROADCAST_NUMBER = re.compile(r'播报编号[：:]\s*([a-f0-9]{12}-[0-9]+)(?![0-9])')
CHINA_TIME = timezone(timedelta(hours=8))


def broadcast_number(text):
    numbers = BROADCAST_NUMBER.findall(text.replace(r'\-', '-'))
    return numbers[-1] if numbers else None


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
        self.owner_resolver = OwnerResolver(self.config)

    def check(self):
        return {'configured': True, 'groupName': self.config['groupName'], 'keyword': self.config['keyword']}

    def __call__(self, payload):
        at = payload.get('at', {})
        ids = at.get('atUserIds', [])
        require('进度播报' in payload['markdown']['text'] and at.get('isAtAll') is False
                and set(at) <= {'isAtAll', 'atUserIds'} and isinstance(ids, list)
                and all(isinstance(uid, str) and USER_ID.fullmatch(uid) for uid in ids), 'ROBOT_MESSAGE_INVALID')
        require(not ids or '整轮验收汇总' not in payload['markdown']['title'], 'SUMMARY_MUST_NOT_MENTION')
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
            return {'outcome': 'accepted' if result['errcode'] == 0 else 'retry', 'code': 'API_' + str(result['errcode'])}
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

    def prepare_failure(self, owners):
        return self.owner_resolver.resolve(owners)

    def confirm_delivery(self, payload, attempted_at):
        number = broadcast_number(payload['markdown']['text'])
        if not number:
            return None
        group_id = self.owner_resolver.resolve_group_id()
        since = datetime.fromtimestamp(attempted_at - 5, CHINA_TIME).strftime('%Y-%m-%d %H:%M:%S')
        for delay in (0, 1, 2):
            if delay:
                time.sleep(delay)
            data = self.owner_resolver.runner([
                'chat', 'message', 'list', '--group', group_id, '--time', since, '--limit', '30',
                '--direction', 'newer', '--page-all', '--page-limit', '3', '--page-delay', '0',
                '--timeout', '4'])
            messages = data.get('messages')
            if messages is None:
                messages = data.get('result', {}).get('messages', [])
            for message in messages:
                message_id = message.get('messageId') or message.get('openMessageId')
                if (message.get('openConversationId', group_id) == group_id
                        and broadcast_number(str(message.get('text') or message.get('content') or '')) == number
                        and message_id and message.get('createTime')):
                    return {'messageId': message_id, 'createdAt': message['createTime']}
        return None
