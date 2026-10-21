"""Requirement-level version progress and a durable notification outbox.

The coordinator records conclusions, never individual testcase completions.
Network delivery is outside the ledger transaction; ambiguous sends need readback.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path
import re
import time

from .core import WorkflowError, atomic_json, canonical_hash, file_hash, read_json, reject_formal_write, require

MODES = {'development': '开发分支详细验收', 'mainline_regression': '主分支回归'}
STATUSES = {'pending', 'running', 'passed', 'failed', 'blocked'}
FINAL = {'passed', 'failed', 'blocked'}
LABELS = {'passed': '通过', 'failed': '未通过', 'blocked': '阻塞'}


def stamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def text(value):
    return isinstance(value, str) and bool(value.strip())


@contextmanager
def locked(root, name='ledger.lock', timeout=10):
    """OS-owned lock releases on process death; the lock file is never deleted."""
    root = Path(root)
    reject_formal_write(root)
    root.mkdir(parents=True, exist_ok=True)
    with (root / name).open('a+b') as stream:
        stream.seek(0, 2)
        if not stream.tell():
            stream.write(b'0'); stream.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                stream.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise WorkflowError('PROGRESS_BUSY') from None
                time.sleep(0.05)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def validate_snapshot(snapshot):
    require(snapshot.get('schemaVersion') == 1, 'SCHEMA_VERSION')
    version = snapshot.get('versionDate')
    require(isinstance(version, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', version), 'VERSION_DATE_INVALID')
    date.fromisoformat(version)
    require(snapshot.get('acceptanceMode') in MODES, 'ACCEPTANCE_MODE_INVALID')
    source = snapshot.get('source', {})
    require(source.get('complete') is True, 'FULL_VERSION_SNAPSHOT_REQUIRED')
    require(all(text(source.get(k)) for k in ('tableId', 'revision', 'capturedAt')), 'SOURCE_REQUIRED')
    require(datetime.fromisoformat(source['capturedAt'].replace('Z', '+00:00')).tzinfo is not None, 'SOURCE_TIMEZONE_REQUIRED')
    items = snapshot.get('items')
    require(isinstance(items, list), 'ITEMS_REQUIRED')
    seen = set()
    for item in items:
        require(text(item.get('id')) and text(item.get('title')) and len(item['title']) <= 500, 'ITEM_INVALID')
        require(item['id'] not in seen, 'DUPLICATE_ITEM')
        seen.add(item['id'])
        require(item.get('status') in STATUSES, 'ITEM_STATUS_INVALID')


def scope(snapshot):
    return [snapshot['source']['tableId'], snapshot['versionDate'], snapshot['acceptanceMode']]


def counts(data):
    values = [i['status'] for i in data['items'].values()]
    return {'total': len(values), 'completed': values.count('passed'), 'pending': values.count('pending'),
            'running': values.count('running'), 'incomplete': values.count('failed') + values.count('blocked')}


def evidence(paths, error='EVIDENCE_REQUIRED'):
    require(isinstance(paths, list) and bool(paths) and all(text(p) for p in paths), error)
    result = []
    for value in paths:
        path = Path(value).resolve()
        require(path.is_file() and path.stat().st_size > 0, error)
        result.append({'path': str(path), 'sha256': file_hash(path)})
    return result


def markdown(value):
    # Titles from documents are data, not Markdown instructions or mentions.
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', ' '.join(str(value).split())).replace('@', '＠')


def message(data, item, sequence, recorded_at):
    c = counts(data)
    title = '进度播报｜' + data['versionDate']
    body = (f'### {title}\n\n验收项：{markdown(item["title"])}\n\n'
            f'验收模式：{MODES[data["acceptanceMode"]]}\n\n本项结果：{LABELS[item["status"]]}\n\n'
            f'总需求：{c["total"]}\n\n已完成：{c["completed"]}\n\n'
            f'待验收：{c["pending"]}｜正在验收：{c["running"]}\n\n未完成：{c["incomplete"]}\n\n'
            f'记录时间：{recorded_at}（北京时间，以上为该时刻进度）\n\n'
            f'播报编号：{canonical_hash(scope(data))[:12]}-{sequence}')
    return {'msgtype': 'markdown', 'markdown': {'title': title, 'text': body}, 'at': {'isAtAll': False}}


class ProgressStore:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = self.root / 'progress.json'

    def read(self):
        data = read_json(self.path)
        require(data.get('schemaVersion') == 1 and isinstance(data.get('items'), dict), 'PROGRESS_INVALID')
        return data

    def initialize(self, snapshot):
        validate_snapshot(snapshot)
        with locked(self.root):
            require(not self.path.exists(), 'PROGRESS_EXISTS')
            data = {k: deepcopy(snapshot[k]) for k in ('schemaVersion', 'versionDate', 'acceptanceMode', 'source')}
            data.update(revision=0, items={i['id']: {**deepcopy(i), 'revision': 0} for i in snapshot['items']},
                        events={}, outbox=[], createdAt=stamp())
            atomic_json(self.path, data)
        return self.status()

    def status(self):
        data = self.read()
        return {'versionDate': data['versionDate'], 'acceptanceMode': data['acceptanceMode'],
                'source': data['source'], 'revision': data['revision'], 'counts': counts(data),
                'items': list(data['items'].values()),
                'notifications': [{k: e.get(k) for k in ('sequence', 'itemId', 'delivery', 'attempts', 'nextAttemptAt', 'code')}
                                  for e in data['outbox']]}

    def sync(self, snapshot):
        validate_snapshot(snapshot)
        with locked(self.root):
            data = self.read()
            require(scope(data) == scope(snapshot), 'SCOPE_MISMATCH')
            require(snapshot.get('expectedRevision') == data['revision'], 'REVISION_CONFLICT')
            incoming = {i['id']: i for i in snapshot['items']}
            if set(incoming) != set(data['items']):
                require(text(snapshot.get('reason')), 'ROSTER_CHANGE_REASON_REQUIRED')
            for ident, item in incoming.items():
                old = data['items'].get(ident)
                if old:
                    require(old['status'] == item['status'], 'SYNC_CANNOT_CHANGE_RESULTS')
                    incoming[ident] = {**old, 'title': item['title']}
                else:
                    require(item['status'] == 'pending', 'NEW_ITEM_MUST_BE_PENDING')
                    incoming[ident] = {**item, 'revision': 0}
            data['rosterHistory'] = data.get('rosterHistory', []) + [
                {'at': stamp(), 'source': data['source'], 'items': data['items'], 'reason': snapshot.get('reason', '')}]
            data.update(items=incoming, source=deepcopy(snapshot['source']), revision=data['revision'] + 1)
            atomic_json(self.path, data)
        return self.status()

    def record(self, request):
        require(text(request.get('eventId')), 'EVENT_ID_REQUIRED')
        request_hash = canonical_hash(request)
        with locked(self.root):
            data = self.read()
            prior = data['events'].get(request['eventId'])
            if prior:
                require(prior['requestHash'] == request_hash, 'EVENT_ID_CONFLICT')
                return {'counts': counts(data), 'revision': data['revision'], 'duplicate': True}
            item = data['items'].get(request.get('itemId'))
            require(item is not None, 'ITEM_NOT_IN_VERSION')
            require(type(request.get('expectedItemRevision')) is int and
                    request['expectedItemRevision'] == item['revision'], 'ITEM_REVISION_CONFLICT')
            status = request.get('status')
            require(status in STATUSES, 'ITEM_STATUS_INVALID')
            proof, conclusion_hash = [], None
            if status in FINAL:
                require(request.get('conclusionFinal') is True and text(request.get('conclusion')), 'FINAL_CONCLUSION_REQUIRED')
                if status == 'passed':
                    require(request.get('scopeComplete') is True, 'SCOPE_INCOMPLETE')
                proof = evidence(request.get('evidence'))
                conclusion_hash = canonical_hash([status, request['conclusion'].strip()])
            at = stamp()
            item.update(status=status, revision=item['revision'] + 1, updatedAt=at)
            data['revision'] += 1
            receipt = {'requestHash': request_hash, 'itemId': item['id'], 'status': status, 'at': at,
                       'evidence': proof, 'conclusion': request.get('conclusion', ''), 'counts': counts(data)}
            if conclusion_hash and conclusion_hash != item.get('lastConclusionHash'):
                seq = len(data['outbox']) + 1
                data['outbox'].append({'sequence': seq, 'itemId': item['id'], 'eventId': request['eventId'],
                                       'recordedAt': at, 'counts': counts(data), 'payload': message(data, item, seq, at),
                                       'delivery': 'pending', 'attempts': 0, 'nextAttemptAt': 0})
                receipt['sequence'] = seq
                item['lastConclusionHash'] = conclusion_hash
            data['events'][request['eventId']] = receipt
            atomic_json(self.path, data)
            return {'counts': counts(data), 'revision': data['revision'], 'event': receipt}

    def flush(self, sender, clock=time.time, limit=5):
        """One bounded drain; future retries run on the next event/resume/flush.

        A crashed sender is recovered as unknown, never blindly retried.
        Holding the sender lock does not block new acceptance result records.
        """
        require(type(limit) is int and 1 <= limit <= 5, 'SEND_LIMIT_INVALID')
        with locked(self.root, 'sender.lock', timeout=0):
            with locked(self.root):
                data = self.read()
                for entry in data['outbox']:
                    if entry['delivery'] == 'sending':
                        entry.update(delivery='unknown', code='INTERRUPTED_SEND')
                atomic_json(self.path, data)
            for _ in range(limit):
                with locked(self.root):
                    data = self.read()
                    current = clock()
                    if current < data.get('sendNotBefore', 0):
                        break
                    recent = [t for t in data.get('attemptTimes', []) if t > current - 60]
                    if len(recent) >= 15:
                        break
                    entry = next((e for e in data['outbox'] if e['delivery'] == 'pending'
                                  and e['nextAttemptAt'] <= current), None)
                    if entry is None:
                        break
                    entry.update(delivery='sending', attempts=entry['attempts'] + 1)
                    sequence, payload = entry['sequence'], deepcopy(entry['payload'])
                    data['attemptTimes'] = recent + [current]
                    atomic_json(self.path, data)  # Durable before network side effects.
                try:
                    response = sender(payload)
                    if not isinstance(response, dict) or response.get('outcome') not in {'sent', 'retry', 'unknown'}:
                        response = {'outcome': 'unknown', 'code': 'INVALID_DELIVERY_RECEIPT'}
                except Exception:
                    response = {'outcome': 'unknown', 'code': 'SEND_EXCEPTION'}
                with locked(self.root):
                    data = self.read()
                    entry = data['outbox'][sequence - 1]
                    outcome = response['outcome']
                    code = str(response.get('code', 'UNSPECIFIED'))
                    entry['code'] = code if re.fullmatch(r'[A-Z0-9_:-]{1,64}', code) else 'REDACTED_ERROR'
                    entry['delivery'] = ('pending' if entry['attempts'] < 3 else 'failed') if outcome == 'retry' else outcome
                    provider_delay = response.get('retryAfterSeconds', 0)
                    provider_delay = provider_delay if type(provider_delay) is int and provider_delay >= 0 else 0
                    entry['nextAttemptAt'] = clock() + max(provider_delay, 30 if entry['attempts'] == 1 else 120)
                    if provider_delay:
                        data['sendNotBefore'] = clock() + provider_delay
                    if outcome == 'sent':
                        entry['sentAt'] = stamp()
                    atomic_json(self.path, data)
        return {'notifications': self.status()['notifications']}

    def resolve(self, request):
        proof = evidence(request.get('evidence'), 'RECONCILIATION_EVIDENCE_REQUIRED')
        require(request.get('outcome') in {'sent', 'not_sent'}, 'RECONCILIATION_OUTCOME_INVALID')
        with locked(self.root, 'sender.lock', timeout=0), locked(self.root):
            data = self.read()
            seq = request.get('sequence')
            require(type(seq) is int and 1 <= seq <= len(data['outbox']), 'MESSAGE_NOT_FOUND')
            entry = data['outbox'][seq - 1]
            require(entry['delivery'] in {'unknown', 'failed'}, 'MESSAGE_NOT_RECONCILABLE')
            entry.setdefault('reconciliations', []).append({'at': stamp(), 'outcome': request['outcome'], 'evidence': proof})
            entry.update(delivery='sent' if request['outcome'] == 'sent' else 'pending', nextAttemptAt=0)
            if request['outcome'] == 'not_sent':
                entry['attempts'] = 0
            atomic_json(self.path, data)
        return self.status()
