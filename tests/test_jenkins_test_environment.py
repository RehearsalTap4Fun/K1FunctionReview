import importlib.util
import json
from pathlib import Path
from threading import Thread
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'review-k1-function/scripts/jenkins_test_environment.py'
JOB = '自定义代码配表分支启动个人远程服'


@pytest.fixture
def jenkins():
    assert SCRIPT.exists(), 'Jenkins test deployment adapter is missing'
    spec = importlib.util.spec_from_file_location('jenkins_test_environment', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def request_data():
    return {'scope': {'environment': 'dev', 'serverIds': ['2650'], 'authorization': 'user message: deploy test server'},
            'sources': {'server': {'ref': 'origin/dev', 'sha': 'a' * 40, 'evidence': 'frozen server manifest'},
                        'config': {'ref': 'origin/dev_coldtest', 'sha': 'b' * 40, 'evidence': 'verified config branch'}},
            'parameters': {'corebranch': 'origin/dev', 'branchName': 'origin/dev_coldtest',
                           'server_id': '2650', 'app': 'gs', 'ALIVE': '5', 'DownKey': ''}}


@pytest.fixture
def api():
    calls = []
    control = {'unknown': False, 'foreign': False}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass

        def reply(self, data, code=200, **headers):
            self.send_response(code)
            for key, value in headers.items(): self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        def do_GET(self):
            calls.append(('GET', self.path, None))
            if '/crumbIssuer/' in self.path:
                self.reply({'crumbRequestField': 'Jenkins-Crumb', 'crumb': 'test-crumb'})
            elif '/queue/item/7/' in self.path:
                url = base + '/job/' + self.server.job_path + '/42/'
                self.reply({'id': 7, 'cancelled': False, 'executable': {'number': 42, 'url': url}})
            elif '/42/api/json' in self.path:
                self.reply({'number': 42, 'building': False, 'result': 'SUCCESS'})
            elif '/job/' in self.path and '/api/json' in self.path:
                defs = []
                for name in ['corebranch', 'branchName', 'server_id', 'DownKey', 'kvk_keep_servers']:
                    defs.append({'name': name, 'type': 'StringParameterDefinition', 'defaultParameterValue': {'value': ''}})
                defs += [{'name': 'app', 'type': 'ChoiceParameterDefinition', 'choices': ['gs', 'battle']},
                         {'name': 'ALIVE', 'type': 'ChoiceParameterDefinition', 'choices': ['1','2','3','4','5']}]
                self.reply({'name': JOB, 'buildable': True, 'property': [{'parameterDefinitions': defs}],
                            'lastBuild': {'number': 999, 'result': 'SUCCESS'}})
            else: self.reply({}, 404)

        def do_POST(self):
            body = self.rfile.read(int(self.headers['Content-Length'])).decode()
            calls.append(('POST', self.path, parse_qs(body, keep_blank_values=True)))
            if control['unknown']:
                self.reply({'private': 'DO_NOT_PRINT'}, 503)
            else:
                self.reply({}, 201, Location=('http://example.invalid/queue/item/7/' if control['foreign'] else base + '/queue/item/7/'))

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    base = 'http://127.0.0.1:' + str(server.server_port) + '/jenkins'
    from urllib.parse import quote
    server.job_path = quote(JOB, safe='')
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield {'baseUrl': base, 'username': 'tester', 'apiToken': 'PRIVATE_TOKEN'}, calls, control
    server.shutdown()
    server.server_close()
    worker.join()


def test_submitted_queue_is_tracked_instead_of_unrelated_latest_build(jenkins, api, request_data, tmp_path):
    config, calls, _ = api
    client = jenkins.Jenkins(config)
    plan = jenkins.prepare(client, request_data)
    receipt_path = tmp_path / 'receipt.json'
    receipt = jenkins.submit(client, plan, receipt_path)
    assert receipt['status'] == 'queued'
    result = jenkins.poll(client, receipt_path)
    assert result['buildNumber'] == 42
    assert result['status'] == 'build_succeeded_runtime_unverified'
    assert not any('lastBuild' in path for _, path, _ in calls)
    posted = [body for method, _, body in calls if method == 'POST']
    assert posted[0]['corebranch'] == ['origin/dev']
    assert posted[0]['branchName'] == ['origin/dev_coldtest']
    assert 'PRIVATE_TOKEN' not in receipt_path.read_text(encoding='utf-8')


@pytest.mark.parametrize('field,value,error', [
    ('server_id','2605','SID_OUT_OF_SCOPE'),
    ('app','battle','SID_APP_MISMATCH'),
    ('ALIVE','9','PARAMETER_CHOICE_INVALID'),
    ('corebranch','origin/not-verified','SOURCE_REF_MISMATCH'),
    ('DownKey','raw-private-key','IMPORT_KEY_MUST_USE_ENV'),
])
def test_bad_deployment_parameters_never_submit(jenkins, api, request_data, field, value, error):
    config, calls, _ = api
    request_data['parameters'][field] = value
    with pytest.raises(jenkins.DeploymentError, match=error): jenkins.prepare(jenkins.Jenkins(config), request_data)
    assert not any(c[0] == 'POST' for c in calls)


def test_unknown_submit_outcome_persists_receipt_and_is_never_reposted(jenkins, api, request_data, tmp_path):
    config, calls, control = api
    client = jenkins.Jenkins(config)
    plan = jenkins.prepare(client, request_data)
    control['unknown'] = True
    path = tmp_path / 'receipt.json'
    with pytest.raises(jenkins.DeploymentError): jenkins.submit(client, plan, path)
    receipt = json.loads(path.read_text(encoding='utf-8'))
    assert receipt['status'] == 'submission_unknown'
    with pytest.raises(jenkins.DeploymentError, match='RECEIPT_EXISTS'): jenkins.submit(client, plan, path)
    assert len([x for x in calls if x[0] == 'POST']) == 1
    assert 'DO_NOT_PRINT' not in path.read_text(encoding='utf-8')


def test_queue_location_must_stay_on_configured_jenkins(jenkins, api, request_data, tmp_path):
    config, calls, control = api
    client = jenkins.Jenkins(config)
    plan = jenkins.prepare(client, request_data)
    control['foreign'] = True
    with pytest.raises(jenkins.DeploymentError, match='UNSAFE_JENKINS_URL'):
        jenkins.submit(client, plan, tmp_path / 'receipt.json')
    assert len([x for x in calls if x[0] == 'POST']) == 1


def test_import_secret_is_read_only_at_submit_and_never_in_receipt(jenkins, api, request_data, tmp_path, monkeypatch):
    config, calls, _ = api
    request_data['dataImportKeyEnv'] = 'K1_TEST_IMPORT_KEY'
    request_data['scope']['dataImportAuthorization'] = 'user approved snapshot import'
    monkeypatch.setenv('K1_TEST_IMPORT_KEY', 'SENSITIVE_DOWNLOAD_KEY')
    client = jenkins.Jenkins(config)
    plan = jenkins.prepare(client, request_data)
    path = tmp_path / 'receipt.json'
    jenkins.submit(client, plan, path)
    assert [c[2] for c in calls if c[0] == 'POST'][0]['DownKey'] == ['SENSITIVE_DOWNLOAD_KEY']
    assert 'SENSITIVE_DOWNLOAD_KEY' not in path.read_text(encoding='utf-8')
    assert 'SENSITIVE_DOWNLOAD_KEY' not in json.dumps(plan)


def test_mutated_scope_or_plan_cannot_be_submitted(jenkins, api, request_data, tmp_path):
    config, calls, _ = api
    client = jenkins.Jenkins(config)
    plan = jenkins.prepare(client, request_data)
    plan['parameters']['server_id'] = '2605'
    with pytest.raises(jenkins.DeploymentError, match='PLAN_CHANGED'):
        jenkins.submit(client, plan, tmp_path / 'receipt.json')
    assert not any(c[0] == 'POST' for c in calls)
