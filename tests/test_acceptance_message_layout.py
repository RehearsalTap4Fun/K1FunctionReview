import importlib
from pathlib import Path

import pytest


@pytest.fixture
def layout(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'review-k1-function/scripts'))
    return importlib.import_module('acceptance.presentation')


def failure(layout, **overrides):
    args = dict(label='600', mode='版本日验收', item={'title': '阵容快照'},
                counters={'total': 3, 'completed': 1, 'pending': 0, 'running': 1, 'incomplete': 1},
                recorded_at='2026-11-06T10:00:00+08:00', event_number='test-1',
                conclusion='重新打开后阵容丢失', display={})
    return layout.failure_message(**{**args, **overrides})['markdown']['text']


def test_failure_contains_details_links_and_only_two_screenshots(layout):
    body = failure(layout, display={'issue': '关闭后丢失', 'expected': '再次打开仍保留',
                                   'environment': 'Unity · 2650 · dev', 'jira': 'NK-100',
                                   'jiraUrl': 'https://jira.example.test/browse/NK-100',
                                   'reportUrl': 'https://report.example.test/result',
                                   'screenshots': [{'url': f'https://images.example.test/{i}.png',
                                                    'caption': f'截图{i}'} for i in range(3)]})
    assert 'failed.png' in body and '验收未通过' in body
    assert '**问题**：关闭后丢失' in body
    assert '**预期**：再次打开仍保留' in body
    assert 'Unity' in body and 'NK\\-100' in body
    assert '[查看报告]' in body
    assert body.count('![截图') == 2
    assert '2.png' not in body
    assert '其余截图见报告' in body
    assert '北京时间' in body


def test_missing_details_do_not_hide_the_failure(layout):
    body = failure(layout)
    assert '重新打开后阵容丢失' in body
    assert '预期待补充' in body and '环境待补充' in body
    assert '暂无可展示截图' in body and '报告链接待补充' in body
    assert 'C:/' not in body


def test_untrusted_markdown_and_local_urls_cannot_add_links(layout):
    body = failure(layout, item={'title': 'A\n@all [click](javascript:alert)'},
                   display={'reportUrl': 'file:///C:/secret/report.html',
                            'screenshots': [{'url': 'data:image/png;base64,test'},
                                            {'url': 'https://images.example.test/a).png',
                                             'caption': '@all ](evil)'}]})
    assert '@all' not in body
    assert '[click](' not in body
    assert 'file:///' not in body and 'data:image' not in body
    assert 'a%29.png' in body


@pytest.mark.parametrize('statuses,banner', [(['passed', 'passed'], 'passed.png'),
                                           (['passed', 'blocked'], 'blocked.png'),
                                           (['failed', 'blocked'], 'failed.png')])
def test_summary_uses_honest_status_color_and_reason_lists(layout, statuses, banner):
    items = [{'title': '需求' + str(i), 'status': status, 'conclusion': '本轮观察结果',
              'display': {'nextStep': '补齐环境再验'}} for i, status in enumerate(statuses)]
    payload = layout.summary_message(label='600', mode='版本日验收', items=items,
                                     round_id='round-1', recorded_at='2026-11-06T10:00:00+08:00',
                                     event_number='test-2',
                                     display={'reportUrl': 'https://report.example.test/result',
                                              'tableUrl': 'https://alidocs.dingtalk.com/i/nodes/test'})
    body = payload['markdown']['text']
    assert banner in body and '整轮验收汇总' in body
    assert '[版本表]' in body and '[完整报告]' in body
    if 'blocked' in statuses:
        assert '补齐环境再验' in body
    if 'failed' in statuses:
        assert '本轮观察结果' in body


def test_summary_limits_long_lists_and_points_to_report(layout):
    items = [{'title': f'需求{i}', 'status': 'failed', 'conclusion': '错误' * 300} for i in range(20)]
    body = layout.summary_message(label='600', mode='版本日验收', items=items, round_id='r',
                                  recorded_at='t', event_number='id', display={})['markdown']['text']
    assert '其余15项见完整报告' in body
    assert len(body.encode('utf-8')) < 12000


def test_banner_override_supports_company_host(layout):
    body = failure(layout, display={'bannerUrls': {'failed': 'https://company.example.test/failed.png'}})
    assert 'https://company.example.test/failed.png' in body


@pytest.mark.parametrize('present,missing', [('tableUrl', '完整报告'), ('reportUrl', '版本表')])
def test_summary_discloses_each_missing_link(layout, present, missing):
    body = layout.summary_message(label='600', mode='版本日验收',
                                  items=[{'title': 'A', 'status': 'passed'}], round_id='r',
                                  recorded_at='t', event_number='id',
                                  display={present: 'https://report.example.test/result'})['markdown']['text']
    assert missing + '链接待补充' in body


def test_footer_converts_utc_to_beijing_time(layout):
    assert '2026\\-11\\-06 10:00:00' in layout.footer('2026-11-06T02:00:00Z', 'id')
