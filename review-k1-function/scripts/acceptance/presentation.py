"""DingTalk Markdown layouts. Render supplied evidence URLs; never upload evidence."""
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlsplit


BANNER_ROOT = ('https://raw.githubusercontent.com/RehearsalTap4Fun/K1FunctionReview/main/'
               'review-k1-function/assets/notification-banners/')


def plain(value, limit=160):
    value = ' '.join(str(value or '').split())
    return value if len(value) <= limit else value[:limit - 1] + '…'


def markdown(value, limit=160):
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', plain(value, limit)).replace('@', '＠')


def web_url(value, image=False):
    if not isinstance(value, str) or len(value) > 4096 or re.search(r'[\s\x00-\x1f]', value):
        return ''
    try:
        parts = urlsplit(value)
        if parts.scheme not in ({'https'} if image else {'http', 'https'}):
            return ''
        if not parts.hostname or parts.username or parts.password:
            return ''
        return quote(value, safe=':/?&=%#;,+$!*-._~')
    except ValueError:
        return ''


def details(value):
    """Ignore malformed optional presentation fields without losing a real result."""
    if not isinstance(value, dict):
        return {}
    result = {k: plain(value.get(k), 500) for k in
              ('issue', 'expected', 'environment', 'jira', 'nextStep', 'screenshotUnavailableReason')
              if value.get(k)}
    for key in ('jiraUrl', 'reportUrl', 'tableUrl'):
        url = web_url(value.get(key))
        if url:
            result[key] = url
    screenshots = value.get('screenshots', [])
    if isinstance(screenshots, list):
        result['screenshots'] = [{'url': web_url(s.get('url'), image=True),
                                  'caption': plain(s.get('caption'), 60)}
                                 for s in screenshots[:20] if isinstance(s, dict)
                                 and web_url(s.get('url'), image=True)]
    banners = value.get('bannerUrls', {})
    if isinstance(banners, dict):
        result['bannerUrls'] = {k: web_url(banners[k], image=True) for k in
                                ('failed', 'passed', 'blocked') if web_url(banners.get(k), image=True)}
    return result


def banner(status, display):
    url = display.get('bannerUrls', {}).get(status) or BANNER_ROOT + status + '.png'
    label = {'failed': '验收未通过', 'passed': '整轮验收通过', 'blocked': '本轮存在阻塞'}[status]
    return f'![{label}]({url})'


def payload(title, blocks):
    return {'msgtype': 'markdown', 'markdown': {'title': title, 'text': '\n\n'.join(blocks)},
            'at': {'isAtAll': False}}


def footer(recorded_at, event_number):
    try:
        parsed = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
        shown = parsed.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S') if parsed.tzinfo else recorded_at
    except (ValueError, TypeError, AttributeError):
        shown = recorded_at
    return f'记录时间：{markdown(shown)}（北京时间） · 播报编号：{markdown(event_number)}'


def failure_message(*, label, mode, item, counters, recorded_at, event_number,
                    conclusion, display=None):
    display = details(display)
    title = '进度播报｜验收未通过｜' + plain(label, 60)
    heading = '**' + markdown(item['title'], 160) + '**'
    if display.get('jira'):
        jira = markdown(display['jira'], 60)
        heading += ' · ' + (f'[{jira}]({display["jiraUrl"]})' if display.get('jiraUrl') else jira)
    blocks = [banner('failed', display), '### ' + markdown(title), heading,
              '**问题**：' + markdown(display.get('issue') or conclusion),
              '**预期**：' + markdown(display.get('expected') or '预期待补充，详见报告'),
              '**环境**：' + markdown(display.get('environment') or '环境待补充，详见报告')
              + ' · ' + markdown(mode)]
    screenshots = display.get('screenshots', [])
    if screenshots:
        blocks.extend(f'![截图{i + 1}：{markdown(s["caption"] or "失败现场", 60)}]({s["url"]})'
                      for i, s in enumerate(screenshots[:2]))
        if len(screenshots) > 2:
            blocks.append('其余截图见报告。')
    else:
        blocks.append('**截图**：暂无可展示截图；' + markdown(
            display.get('screenshotUnavailableReason') or '请在报告中核对证据缺口。'))
    blocks.append(f'[查看报告]({display["reportUrl"]})' if display.get('reportUrl') else '报告链接待补充。')
    blocks.extend([f'总需求：{counters["total"]}｜已完成：{counters["completed"]}｜未完成：{counters["incomplete"]}'
                   f'\n\n待验收：{counters["pending"]}｜正在验收：{counters["running"]}',
                   footer(recorded_at, event_number)])
    return payload(title, blocks)


def summary_message(*, label, mode, items, round_id, recorded_at, event_number, display=None):
    display = details(display)
    groups = {s: [i for i in items if i['status'] == s] for s in ('passed', 'failed', 'blocked')}
    color = 'failed' if groups['failed'] else 'blocked' if groups['blocked'] else 'passed'
    title = '进度播报｜整轮验收汇总｜' + plain(label, 60)
    blocks = [banner(color, display), '### ' + markdown(title),
              f'**通过：{len(groups["passed"])}｜未通过：{len(groups["failed"])}｜阻塞：{len(groups["blocked"])}**',
              f'本轮总需求：{len(items)} · {markdown(mode)}\n\n验收批次：{markdown(round_id, 100)}']
    for status, label in [('failed', '未通过'), ('blocked', '阻塞')]:
        if not groups[status]:
            continue
        lines = []
        for item in groups[status][:5]:
            extra = details(item.get('display'))
            reason = extra.get('issue') or item.get('conclusion') or '原因详见报告'
            line = '- ' + markdown(item['title'], 60) + '：' + markdown(reason, 80)
            if status == 'blocked':
                line += '；下一步：' + markdown(extra.get('nextStep') or '待明确补验动作', 80)
            lines.append(line)
        if len(groups[status]) > 5:
            lines.append(f'- 其余{len(groups[status]) - 5}项见完整报告。')
        blocks.append('**' + label + '**\n\n' + '\n'.join(lines))
    links = [f'[{name}]({display[key]})' if display.get(key) else name + '链接待补充'
             for key, name in [('tableUrl', '版本表'), ('reportUrl', '完整报告')]]
    blocks.append(' · '.join(links))
    blocks.append(footer(recorded_at, event_number))
    return payload(title, blocks)
