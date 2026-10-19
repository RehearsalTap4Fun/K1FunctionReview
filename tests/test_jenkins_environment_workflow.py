"""Protocol fixtures for the backup → DingTalk → deployment → runtime contract."""
import importlib.util
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
from urllib.parse import parse_qs, unquote, urlsplit

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'review-k1-function/scripts'
sys.path.insert(0, str(SCRIPTS))
SECRET = 'fixture-private-down-key-0123456789'


@pytest.fixture
def flow():
    path = SCRIPTS / 'jenkins_environment_workflow.py'
    assert path.exists(), 'Backup-to-runtime workflow is missing'
    spec = importlib.util.spec_from_file_location('jenkins_environment_workflow', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def message(sid='2650', key=SECRET, identifier='message-1', when=None):
    return {'openMessageId': identifier, 'openConversationId': 'group-1', 'sendType': 'robot',
            'senderOpenDingTalkId': 'robot-1',
            'sender': 'fixture-backup-robot', 'createTime': when or datetime.now(timezone.utc).isoformat(),
            'content': "#### k1 Prod DB 备份数据库\n备份游戏: ['" + sid + "']\n备份下载命令: file-ladder down " + key + '\n状态: **完成**'}


def request(sid='2650', **extra):
    return {'onlineSid': sid, 'codeBranch': 'dev', 'configBranch': 'dev_kvk',
            'authorization': '本会话用户明确要求备份并导入重建本人测试服', **extra}


def sources():
    return {'server': {'ref': 'origin/dev', 'sha': 'a' * 40, 'evidence': 'manifest.json#server'},
            'config': {'ref': 'origin/dev_kvk', 'sha': 'b' * 40, 'evidence': 'manifest.json#config'}}


class Protocol:
    """External protocol fixtures; records every mutation, no actual services."""
    base = 'http://jenkins.test/jenkins'

    def __init__(self, flow):
        self.f = flow
        self.posts = []
        self.builds = {}
        self.queues = {}
        self.messages = []
        self.unknown = False
        self.containers = []
        self.revision = 'a' * 40
        self.ready = True

    def safe_url(self, url):
        assert url.startswith(self.base + '/')
        return url

    def inspect(self):
        names = ['corebranch', 'branchName', 'app', 'server_id', 'ALIVE', 'DownKey', 'kvk_keep_servers']
        return {'buildable': True, 'parameters': {x: {'name': x} for x in names}}

    def get(self, url, tree=None):
        path = unquote(urlsplit(url).path)
        if '/crumbIssuer/' in path:
            return {'crumbRequestField': 'Jenkins-Crumb', 'crumb': 'fixture'}
        if '/queue/item/' in path:
            qid = int(path.split('/item/')[1].split('/')[0])
            if qid not in self.queues:
                raise self.f.DeploymentError('JENKINS_HTTP_404')
            return self.queues[qid]
        if path.endswith('/queue/api/json'):
            return {'items': []}
        job = path.split('/job/')[1].split('/')[0]
        if path.endswith('/job/' + job + '/api/json'):
            items = sorted([v for (j, _), v in self.builds.items() if j == job], key=lambda v: v['number'], reverse=True)
            return {'name': job, 'buildable': True, 'property': [{'parameterDefinitions': [{'name': 'sid'}]}],
                    'allBuilds': items, 'firstBuild': {'number': items[-1]['number']} if items else None}
        number = int(path.split('/job/')[1].split('/')[1])
        return deepcopy(self.builds[(job, number)])

    def request(self, url, data=None, headers=None):
        if data is None:
            if self.f.BACKUP_PATH in url:
                console = '{"workflow":{"$oid":"abc123abc123abc123abc123"},"url":"https://oops.tap4fun.com/-/workflows/abc123abc123abc123abc123"}'
            elif self.f.job_path(self.f.CHILD_JOB) in url:
                console = '441887 document(s) restored successfully. 0 document(s) failed to restore.'
            else:
                console = 'Starting building: 个人远程服务器部署 #301'
            return 200, {}, console.encode()
        job = unquote(url.split('/job/')[1].split('/')[0])
        params = {k: v[0] for k, v in parse_qs(data.decode(), keep_blank_values=True).items()}
        self.posts.append((job, params))
        number = 101 if job == self.f.BACKUP_JOB else 201
        qid = number + 1
        build = {'number': number, 'url': self.base + self.f.job_path(job) + str(number) + '/',
                 'queueId': qid, 'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                 'duration': 1, 'building': False, 'result': 'SUCCESS',
                 'actions': [{'parameters': [{'name': k, 'value': v} for k, v in params.items()],
                              'causes': [{'userId': 'tester'}]}]}
        if job == self.f.DEPLOY_JOB:
            for repo, sha in [('game', self.revision), ('dataconfig', 'b' * 40)]:
                build['actions'].append({'remoteUrls': ['ssh://git/k1/' + repo + '.git'], 'lastBuiltRevision': {'SHA1': sha}})
            cp = {'APP': params['app'], 'SID': params['server_id'], 'DB_TAG': 'dev' + params['server_id'],
                  'NACOS': 'dev', 'BRANCH': params['corebranch'], 'DownKey': params['DownKey'],
                  'KVK_KEEP_SERVERS': params['kvk_keep_servers']}
            self.builds[(self.f.CHILD_JOB, 301)] = {**build, 'number': 301,
                'actions': [{'parameters': [{'name': k, 'value': v} for k, v in cp.items()],
                             'causes': [{'upstreamProject': job, 'upstreamBuild': number}]}]}
        self.builds[(job, number)] = build
        self.queues[qid] = {'id': qid, 'executable': {'number': number, 'url': build['url']}}
        if self.unknown:
            self.unknown = False
            raise self.f.DeploymentError('JENKINS_NETWORK_ERROR')
        return 201, {'Location': self.base + '/queue/item/' + str(qid) + '/'}, b''

    def read_messages(self, group, since):
        return deepcopy(self.messages)

    def probe(self, plan, runtime=False):
        now = datetime.now(timezone.utc)
        sid, app = plan['request']['targetSid'], plan['request']['app']
        child = self.builds.get((self.f.CHILD_JOB, 301))
        started = datetime.fromtimestamp(child['timestamp'] / 1000, timezone.utc) if child else now
        return {'checkedAt': now.isoformat(), 'host': '192.0.2.10', 'inventoryComplete': True,
                'containers': deepcopy(self.containers),
                'container': {'name': 'remote-tester-' + app + '-' + sid, 'running': self.ready,
                              'startedAt': started.isoformat(), 'image': 'k1-dev:' + self.revision[:12],
                              'command': ['game', '--nacos=dev', '--csv=dev' + sid, '--sid=' + sid] + (['--battle'] if app == 'battle' else []),
                              'processRunning': True, 'imageId': 'sha256:fixture'},
                'heartbeat': {'type': 'game' if app == 'gs' else 'battle', 'sid': int(sid), 'running': True,
                              'runningTime': int(now.timestamp() * 1000), 'ip': '192.0.2.10', 'mainPort': 22650,
                              'codeVer': 'origin/dev(tester)', 'timeOffsetSec': 0},
                'tcp': [{'host': '192.0.2.10', 'port': 22650, 'reachable': True}]}


@pytest.fixture
def setup(flow, tmp_path):
    protocol = Protocol(flow)
    config = {'baseUrl': protocol.base, 'username': 'tester', 'apiToken': 'unused',
              'deploymentDefaults': {'ALIVE': '5'}, 'environmentWorkflow': {'runtimeHost': '192.0.2.10', 'sender': 'fixture-backup-robot', 'groupId': 'group-1', 'senderId': 'robot-1'}}
    plan = flow.prepare_plan(request(), sources(), config)
    flow.write_new(tmp_path / 'workflow.json', plan)
    return protocol, plan, tmp_path


def test_backup_to_runtime_and_resume_never_duplicates_or_persists_key(flow, setup):
    p, plan, root = setup
    result = flow.advance(p, plan, root, p)
    assert len(p.posts) == 1 and p.posts[0] == (flow.BACKUP_JOB, {'sid': '2650'})
    assert result['status'] != 'ready'
    p.messages = [message()]
    for _ in range(6):
        result = flow.advance(p, plan, root, p)
    assert result['status'] == 'ready'
    assert [x[0] for x in p.posts] == [flow.BACKUP_JOB, flow.DEPLOY_JOB]
    assert p.posts[1][1]['DownKey'] == SECRET
    assert p.posts[1][1]['branchName'] == 'origin/dev_kvk'
    assert SECRET not in '\n'.join(x.read_text(encoding='utf-8') for x in root.glob('*.json'))
    assert result['featureAcceptance'] == 'not_performed'


@pytest.mark.parametrize('sid,extra,app,keep', [('2650', {}, 'gs', ''), ('10007', {}, 'battle', ''),
    ('10007', {'kvk_keep_servers': ['2650', '2651']}, 'battle', '2650,2651')])
def test_restore_defaults_and_explicit_battle_retention(flow, sid, extra, app, keep):
    result = flow.normalize_request(request(sid, **extra), {'ALIVE': '5'})
    assert result['app'] == app and result['targetSid'] == sid
    assert result['kvk_keep_servers'] == keep and result['aliveDays'] == '5'


@pytest.mark.parametrize('extra', [{'kvk_keep_servers': []}, {'kvk_keep_servers': ['bad']},
    {'app': 'gs'}, {'targetSid': '2650'}, {'unexpected': 'ignored?'}])
def test_invalid_request_never_silently_changes_restore_scope(flow, extra):
    with pytest.raises(flow.DeploymentError):
        flow.normalize_request(request('10007', **extra), {})


def test_submission_timeout_reconciles_same_build_without_reposting(flow, setup):
    p, plan, root = setup
    p.unknown = True
    with pytest.raises(flow.DeploymentError, match='NETWORK'):
        flow.advance(p, plan, root, p)
    p.messages = [message()]
    for _ in range(6):
        result = flow.advance(p, plan, root, p)
    assert result['status'] == 'ready'
    assert len(p.posts) == 2


def test_ambiguous_completion_and_other_owner_block_deployment(flow, setup):
    p, plan, root = setup
    flow.advance(p, plan, root, p)
    p.messages = [message(), message(identifier='message-2')]
    with pytest.raises(flow.DeploymentError, match='AMBIGUOUS'):
        flow.advance(p, plan, root, p)
    assert len(p.posts) == 1
    p.messages = [message()]
    p.containers = ['remote-someone-else-gs-2650']
    with pytest.raises(flow.DeploymentError, match='OCCUPIED'):
        flow.advance(p, plan, root, p)
    assert len(p.posts) == 1


def test_stale_wrong_group_wrong_sid_messages_are_not_keys(flow, setup):
    p, plan, root = setup
    flow.advance(p, plan, root, p)
    wrong_group = message(); wrong_group['openConversationId'] = 'other'
    p.messages = [message(sid='26501'), message(when='2001-01-01T00:00:00+00:00'), wrong_group]
    result = flow.advance(p, plan, root, p)
    assert result['status'] == 'waiting_backup_message'
    assert len(p.posts) == 1


def test_build_success_with_moved_revision_never_marks_ready(flow, setup):
    p, plan, root = setup
    flow.advance(p, plan, root, p)
    p.messages = [message()]
    p.revision = 'c' * 40
    flow.advance(p, plan, root, p)
    with pytest.raises(flow.DeploymentError, match='REVISION'):
        flow.advance(p, plan, root, p)


@pytest.mark.parametrize('change', ['stopped', 'stale', 'wrong_sid', 'closed_port', 'old_container', 'wrong_config'])
def test_runtime_proof_requires_current_matching_process_heartbeat_and_socket(flow, setup, change):
    p, plan, _ = setup
    data = p.probe(plan, True)
    if change == 'stopped': data['container']['processRunning'] = False
    if change == 'stale': data['heartbeat']['runningTime'] = 1
    if change == 'wrong_sid': data['heartbeat']['sid'] = 2651
    if change == 'closed_port': data['tcp'][0]['reachable'] = False
    if change == 'old_container': data['container']['startedAt'] = '2001-01-01T00:00:00+00:00'
    if change == 'wrong_config': data['container']['command'][2] = '--csv=dev2651'
    with pytest.raises(flow.DeploymentError):
        flow.verify_runtime(plan, data, datetime.now(timezone.utc).timestamp() - 10)


def test_real_docker_nanosecond_timestamp_is_supported(flow):
    assert flow.seconds('2026-10-19T10:17:45.899402007Z') == pytest.approx(1792405065.899402)


def test_battle_uses_game_process_with_battle_flag(flow, tmp_path):
    p = Protocol(flow)
    plan = flow.prepare_plan(request('10007'), sources(), {'baseUrl': p.base, 'username': 'tester', 'environmentWorkflow': {'runtimeHost': '192.0.2.10', 'sender': 'fixture-backup-robot', 'groupId': 'group-1', 'senderId': 'robot-1'}})
    data = p.probe(plan, True)
    flow.verify_runtime(plan, data, datetime.now(timezone.utc).timestamp() - 10)
    data['container']['command'].remove('--battle')
    with pytest.raises(flow.DeploymentError, match='CONFIGURATION'):
        flow.verify_runtime(plan, data, datetime.now(timezone.utc).timestamp() - 10)


def test_unknown_submission_cannot_claim_later_manual_build(flow, setup):
    p, plan, root = setup
    p.unknown = True
    with pytest.raises(flow.DeploymentError):
        flow.advance(p, plan, root, p)
    p.builds[(flow.BACKUP_JOB, 101)]['timestamp'] += 3600000
    p.queues.clear()
    with pytest.raises(flow.DeploymentError, match='RECONCILIATION'):
        flow.advance(p, plan, root, p)
    assert len(p.posts) == 1


def test_failed_oops_receipt_stops_waiting_and_saves_no_secret(flow, setup):
    p, plan, root = setup
    flow.advance(p, plan, root, p)
    failed = message(); failed['content'] = failed['content'].replace('完成', '失败')
    p.messages = [failed]
    with pytest.raises(flow.DeploymentError, match='BACKUP_WORKFLOW_FAILED'):
        flow.advance(p, plan, root, p)
    saved = (root / 'backup-failure.json').read_text(encoding='utf-8')
    assert 'message-1' in saved and SECRET not in saved
    assert len(p.posts) == 1


def test_second_precision_dingtalk_completion_at_build_start(flow, setup):
    _, plan, _ = setup
    when = '2026-10-19T10:00:00+00:00'
    start = flow.seconds(when) + .5
    assert len(flow.backup_messages([message(when=when)], plan, start, start + 1)) == 1


def test_old_run_cannot_claim_later_container_or_later_config_deployment(flow, setup):
    p, plan, root = setup
    flow.advance(p, plan, root, p)
    p.messages = [message()]
    flow.advance(p, plan, root, p)
    flow.advance(p, plan, root, p)
    old = p.builds[(flow.DEPLOY_JOB, 201)]
    later = deepcopy(old)
    later.update(number=202, timestamp=old['timestamp'] + 60000)
    later['actions'][-1]['lastBuiltRevision']['SHA1'] = 'c' * 40
    p.builds[(flow.DEPLOY_JOB, 202)] = later
    with pytest.raises(flow.DeploymentError, match='SUPERSEDED'):
        flow.advance(p, plan, root, p)
    p.builds.pop((flow.DEPLOY_JOB, 202))
    probe = p.probe(plan, True)
    probe['container']['startedAt'] = datetime.fromtimestamp(old['timestamp'] / 1000 + 60, timezone.utc).isoformat()
    with pytest.raises(flow.DeploymentError, match='NOT_CURRENT'):
        flow.verify_runtime(plan, probe, old['timestamp'] / 1000, old['timestamp'] / 1000 + 1)


def test_prior_backups_cannot_share_one_second_precision_receipt(flow, setup):
    p, plan, _ = setup
    start = int(datetime.now(timezone.utc).timestamp()) - 60
    for number, delta in [(90, 100), (91, 800)]:
        p.builds[(flow.BACKUP_JOB, number)] = {'number': number, 'timestamp': start * 1000 + delta,
            'building': False, 'result': 'SUCCESS', 'actions': [{'parameters': [{'name': 'sid', 'value': '2650'}]}]}
    p.messages = [message(when=datetime.fromtimestamp(start, timezone.utc).isoformat())]
    with pytest.raises(flow.DeploymentError, match='PREVIOUS_BACKUP_COMPLETION_UNPROVEN'):
        flow.backup_preflight(p, plan, p)


def test_dws_pagination_deduplicates_overlap_and_rejects_stalled_boundary(flow, monkeypatch):
    first = message(when='2026-10-19T10:00:01+00:00')
    second = message(identifier='message-2', when='2026-10-19T10:00:02+00:00')
    pages = iter([{'success': True, 'result': {'messages': [first], 'hasMore': True}},
                  {'success': True, 'result': {'messages': [first, second], 'hasMore': False}}])
    monkeypatch.setattr(flow, 'capture_json', lambda *a: next(pages))
    service = flow.Services.__new__(flow.Services); service.dws = 'fixture-dws'
    assert len(service.read_messages('group-1', flow.seconds('2026-10-19T10:00:00+00:00'))) == 2
    monkeypatch.setattr(flow, 'capture_json', lambda *a: {'success': True, 'result': {'messages': [first], 'hasMore': True}})
    with pytest.raises(flow.DeploymentError, match='PAGINATION_STALLED'):
        service.read_messages('group-1', flow.seconds(first['createTime']))


def test_probe_extracts_only_target_heartbeat_and_never_raw_log_secrets():
    import k1_environment_probe as probe
    raw = 'mongodb://user:PRIVATE_PASSWORD@host/db\nHSet(gm:cluster:battle:list,10007,'
    value = {'type': 'battle', 'sid': 10007, 'runningTime': 10, 'running': True, 'password': SECRET}
    heartbeat = probe.heartbeat_from_logs(raw + json.dumps(value) + ')', '10007', 'battle')
    assert heartbeat['sid'] == 10007
    assert SECRET not in json.dumps(heartbeat) and 'password' not in heartbeat
    assert probe.heartbeat_from_logs(raw + json.dumps(value), '10008', 'battle') == {}


def test_same_display_name_from_different_robot_is_not_a_backup(flow, setup):
    _, plan, _ = setup
    spoof = message()
    spoof['senderOpenDingTalkId'] = 'different-robot'
    assert flow.backup_messages([spoof], plan, 0, datetime.now(timezone.utc).timestamp() + 1) == []


@pytest.mark.parametrize('extra,keep', [({}, ''), ({'kvk_keep_servers': ['2650', '2651']}, '2650,2651')])
def test_battle_full_chain_passes_exact_restore_scope_to_child(flow, tmp_path, extra, keep):
    p = Protocol(flow)
    plan = flow.prepare_plan(request('10007', **extra), sources(), {'baseUrl': p.base, 'username': 'tester',
        'environmentWorkflow': {'runtimeHost': '192.0.2.10', 'sender': 'fixture-backup-robot', 'groupId': 'group-1', 'senderId': 'robot-1'}})
    flow.write_new(tmp_path / 'workflow.json', plan)
    flow.advance(p, plan, tmp_path, p)
    p.messages = [message(sid='10007')]
    flow.advance(p, plan, tmp_path, p)
    evidence = flow.advance(p, plan, tmp_path, p)
    assert p.posts[0] == (flow.BACKUP_JOB, {'sid': '10007'})
    assert p.posts[1][1]['app'] == 'battle'
    assert p.posts[1][1]['kvk_keep_servers'] == keep
    assert evidence['status'] == 'ready'
