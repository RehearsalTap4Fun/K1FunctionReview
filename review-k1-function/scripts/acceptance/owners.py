"""Resolve responsible handlers to verified group members; never guess an identity."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from .core import require
from .presentation import markdown


USER_ID = re.compile(r'[A-Za-z0-9_-]{1,128}')


def owner_names(value):
    values = [value] if isinstance(value, str) else value if isinstance(value, list) else []
    return list(dict.fromkeys(part.strip() for v in values if isinstance(v, str)
                              for part in re.split(r'[、,，;；\r\n]+', v) if part.strip()))


def dws_call(args):
    binary = os.environ.get('K1_DWS_EXECUTABLE') or shutil.which('dws')
    if not binary:
        local = Path.home() / '.local/bin/dws.exe'
        binary = str(local) if local.is_file() else 'dws'
    result = subprocess.run([binary, *args, '--format', 'json'], capture_output=True,
                            encoding='utf-8', timeout=15, check=True)
    data = json.loads(result.stdout.lstrip('\ufeff'))
    require(isinstance(data, dict) and data.get('success') is True, 'OWNER_LOOKUP_UNAVAILABLE')
    return data


class OwnerResolver:
    def __init__(self, config, runner=dws_call):
        self.config, self.runner = config, runner
        self.group_id, self.members = None, None
        self.people = {}

    def pages(self, prefix, key):
        values, cursor, seen = [], '0', set()
        while True:
            require(cursor not in seen, 'OWNER_LOOKUP_UNAVAILABLE')
            seen.add(cursor)
            data = self.runner([*prefix, '--cursor', cursor])
            require(data.get('success') is True, 'OWNER_LOOKUP_UNAVAILABLE')
            result = data.get('result', {})
            require(isinstance(result, dict), 'OWNER_LOOKUP_UNAVAILABLE')
            page = result.get(key, result.get('value') if key == 'groups' else None)
            require(isinstance(page, list), 'OWNER_LOOKUP_UNAVAILABLE')
            values.extend(page)
            if result.get('hasMore') is False:
                return values
            require(result.get('hasMore') is True and bool(result.get('nextCursor')), 'OWNER_LOOKUP_UNAVAILABLE')
            cursor = str(result['nextCursor'])

    def group_members(self):
        if self.members is not None:
            return self.members
        group_id = self.config.get('openConversationId')
        if not group_id:
            groups = self.pages(['chat', 'search', '--query', self.config['groupName']], 'groups')
            matches = {g.get('openConversationId') for g in groups if g.get('title') == self.config['groupName']}
            require(len(matches) == 1 and None not in matches, 'OWNER_GROUP_AMBIGUOUS')
            group_id = matches.pop()
        members = self.pages(['chat', 'group', 'members', '--id', group_id], 'list')
        self.group_id, self.members = group_id, members
        return members

    def resolve(self, value):
        names = owner_names(value)
        result = {'userIds': [], 'resolved': [], 'unresolved': []}
        if not names:
            result['unresolved'].append({'name': '负责人', 'code': 'OWNER_MISSING'})
            return result
        for name in names:
            code, selected = None, None
            try:
                if re.search(r'\[\s*x\s*\]$', name, re.I):
                    code = 'OWNER_INACTIVE'
                else:
                    members = self.group_members()
                    matching = {m.get('openDingtalkId') for m in members}
                    matching.discard(None)
                    if not matching:
                        code = 'OWNER_NOT_IN_GROUP'
                    else:
                        if name not in self.people:
                            response = self.runner(['aisearch', 'person', '--keyword', name, '--dimension', 'name'])
                            require(response.get('success') is True and isinstance(response.get('result'), list),
                                    'OWNER_LOOKUP_UNAVAILABLE')
                            require(response.get('hasMore') is not True, 'OWNER_LOOKUP_UNAVAILABLE')
                            self.people[name] = response['result']
                        candidates = set()
                        for person in self.people[name]:
                            labels = [person.get('title'), person.get('meta', {}).get('name')]
                            labels += person.get('_searchEvidence', {}).get('aliases', [])
                            uid, oid = person.get('userId'), person.get('openDingTalkId')
                            if name in labels and isinstance(uid, str) and USER_ID.fullmatch(uid) and isinstance(oid, str):
                                candidates.add((uid, oid))
                        pairs = {(uid, oid) for uid, oid in candidates if oid in matching}
                        if len(pairs) == 1:
                            selected = pairs.pop()
                        else:
                            code = ('OWNER_AMBIGUOUS' if len(pairs) > 1 else
                                    'OWNER_NOT_IN_GROUP' if candidates else 'OWNER_ID_UNCONFIRMED')
            except Exception:
                code = 'OWNER_LOOKUP_UNAVAILABLE'
            if selected:
                uid, oid = selected
                if uid not in result['userIds']:
                    result['userIds'].append(uid)
                    result['resolved'].append({'name': name, 'userId': uid, 'openDingTalkId': oid})
            else:
                result['unresolved'].append({'name': name, 'code': code})
        if self.group_id:
            result['openConversationId'] = self.group_id
        return result


def apply_mentions(payload, resolution):
    result = deepcopy(payload)
    ids = list(dict.fromkeys(uid for uid in resolution.get('userIds', [])
                             if isinstance(uid, str) and USER_ID.fullmatch(uid)))
    result['at'] = {'atUserIds': ids, 'isAtAll': False} if ids else {'isAtAll': False}
    lines = ['**负责人**：' + ' '.join('@' + uid for uid in ids)] if ids else []
    labels = {'OWNER_MISSING': '未填写', 'OWNER_INACTIVE': '已停用', 'OWNER_NOT_IN_GROUP': '不在接收群',
              'OWNER_AMBIGUOUS': '重名未确认', 'OWNER_ID_UNCONFIRMED': '身份未核实',
              'OWNER_LOOKUP_UNAVAILABLE': '身份查询不可用'}
    if resolution.get('unresolved'):
        missing = '、'.join(markdown(i.get('name', '负责人'), 80) + '（' +
                           labels.get(i.get('code'), '身份未核实') + '）' for i in resolution['unresolved'])
        lines.append('**未能定向提醒**：' + missing)
    notice = '\n\n'.join(lines)
    body = result['markdown']['text']
    marker = '\n\n**问题**：'
    result['markdown']['text'] = body.replace(marker, '\n\n' + notice + marker, 1) if marker in body else body + '\n\n' + notice
    return result
