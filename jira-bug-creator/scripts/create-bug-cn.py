# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = ["atlassian-python-api>=3.41.0", "python-dotenv>=1.0.0", "requests>=2.31.0"]
# ///
"""
创建 Jira Bug 单 (智能版)

特性:
1. 自动分析 Bug 描述 → 判断应分给哪个部门
2. 从需求单自定义字段获取该部门的负责人
3. 智能缓存：功能名 → 负责人映射
4. 版本号智能优先级（4级）：显式指定 → 归属功能版本 → Git分支 → 动态获取
5. 特殊规则处理：Firebase报错、合服相关自动使用常规功能
6. 智能提取核心功能名：去除描述性词汇，简化标题
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv
from atlassian import Jira
import requests
from requests.auth import HTTPBasicAuth

# 添加 lib 路径
sys.path.insert(0, str(Path(__file__).parent))

# 添加 feature-owner-map skill 路径 (同级 skills 目录)
FEATURE_OWNER_MAP_PATH = Path(__file__).parent.parent.parent / 'feature-owner-map' / 'scripts'
if FEATURE_OWNER_MAP_PATH.exists():
    sys.path.insert(0, str(FEATURE_OWNER_MAP_PATH))
    try:
        from lookup import OwnerLookup
        OWNER_LOOKUP_AVAILABLE = True
    except (ImportError, Exception) as e:
        # 可能缺少依赖，忽略
        OWNER_LOOKUP_AVAILABLE = False
else:
    OWNER_LOOKUP_AVAILABLE = False


# ========== 配置 ==========

# Bug 等级选项 ID
BUG_LEVEL_IDS = {'A': '10104', 'B': '10105', 'C': '10106', 'D': '10107'}

# 重现概率选项 ID (NK 项目)
REPRODUCE_RATE_IDS = {
    'Always': '10010',   # 必现
    'High': '10013',     # 偶现高
    'Medium': '10025',   # 偶现中
    'Low': '10008',      # 偶现低
    'Once': '10011',     # 一次
}

# 岗位字段映射 (从 feature-owners skill)
ROLE_FIELDS = {
    "策划": "customfield_12118",  # 需求审核人(策划)
    "UI": "customfield_12119",    # 需求审核人(UI)
    "UX": "customfield_12127",    # 需求审核人(UX)
    "GUI": "customfield_10209",   # GUI负责人
    "客户端": "customfield_12107", # 需求审核人(客户端)
    "服务器": "customfield_12122", # 需求审核人(服务端)
    "测试": "customfield_12116",  # 跟进QA
}

# 部门 Leader - 从 Config 类动态获取，支持多项目 (K1, X1)
# 此变量作为空配置时的 fallback
LEADERS = {
    '策划': '',
    '客户端': '',
    '服务器': '',
    '运营': '',
    '测试': '',
}

# 默认归属功能 - 从 Config 类动态获取，支持多项目
DEFAULT_RELATED_FUNCTION = ''

# GitLab 配置
GITLAB_URL = 'https://git.tap4fun.com'
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', '')
# GITLAB_PROJECT 从 Config 类动态获取
GITLAB_PROJECT = ''

# 分支类型 → 版本映射
BRANCH_VERSION_MAPPING = {
    'online': ['master', 'master_last', 'master_bugfix'],  # 线上分支
    'development': ['dev', 'hotfix']  # 开发分支
}

# 已完成状态列表
COMPLETED_STATUSES = {'已完成', 'Done', 'Closed', '已关闭', '完成'}

# 特殊功能归属规则 (跳过查找测试单,直接使用常规功能)
SPECIAL_FEATURE_RULES = {
    '合服': DEFAULT_RELATED_FUNCTION,
    '合服后': DEFAULT_RELATED_FUNCTION,
}

# Bug 描述关键词 → 部门映射 (用于自动分析)
DEPT_KEYWORDS = {
    '策划': ['策划', '数值', '配置', '规则', '逻辑', '玩法', '需求', '公式', '文案错误', '描述错误'],
    '客户端': ['客户端', '前端', '性能', '卡顿', '崩溃', 'crash', '闪退', '报错', '异常', 'bug', '代码', '点击无响应', '无响应', '点击无效', '无法点击', '点击无反应', '选中', '选择错误', '选错', '实际选中', '挂了', '界面挂了', '显示错乱', '显示异常', '界面异常', '显示错误', '界面', '显示', '文字', '布局', '图标', '按钮', '弹窗', '空白', '闪烁', '错位', '重叠'],
    '服务器': ['服务器', '后端', '服务端', '数据', '同步', '网络', '延迟', '丢失', '存档', '合服', '合服后', '数据错误', '数据异常'],
    '运营': ['运营', '活动', '公告', '邮件', '礼包', '充值', '支付', '商城', '推送'],
}


def valid_name(v):
    """从版本对象或字符串中提取版本名"""
    if isinstance(v, dict):
        return v.get('name', '')
    return str(v)


def is_firebase_crash(description: str, summary: str = '') -> bool:
    """
    判断是否为 Firebase 报错

    Firebase 报错特殊规则:
    - 归属功能: X2-39092 (常规功能)
    - Bug 等级: C级 (默认)
    - 部门: 客户端
    """
    text = f"{description} {summary}".lower()
    firebase_keywords = [
        'firebase',
        'crashlytics',
        'console.firebase.google.com',
        'nullreferenceexception',
    ]
    return any(kw in text for kw in firebase_keywords)


def extract_core_feature_name(feature: str) -> str:
    """
    提取核心功能名，去除描述性词汇

    规则：提取第一个核心功能名，去除子功能、属性、描述词

    例如:
    - "机甲变色" → "机甲"
    - "联盟旗帜外观" → "联盟"
    - "NPC气泡" → "NPC"
    - "付费墙显示相关" → "付费墙"
    - "大航海界面刷新" → "大航海"
    """
    if not feature:
        return feature

    # 完整功能名（多词）：若描述中包含则保留不截断
    full_feature_names = ['联盟卡牌战斗', '挖矿小游戏', '大航海']
    for name in full_feature_names:
        if name in feature:
            return name

    # 主模块+属性/子功能时只取第一个词（机甲、NPC 等）
    single_word_modules = ['机甲', 'NPC', '英雄', '建筑', '军备', '武器', '存钱罐']
    for module in single_word_modules:
        if feature.startswith(module):
            return module

    # 去除常见描述性词汇（保留主体名称）
    remove_words = [
        '显示', '刷新', '旋转', '相关', '外观', '界面',
        '功能', '模块', '系统', '的', '在', '时', '后',
        '变色', '气泡', '旗帜', '队列', '主界面'
    ]

    result = feature
    for word in remove_words:
        result = result.replace(word, '')

    return result.strip() or feature  # 如果全部去除后为空，返回原始名称


class SmartBugCreator:
    """智能 Bug 创建器 - 支持多项目"""

    def __init__(self, project: str = None):
        """
        初始化 Bug 创建器

        Args:
            project: 项目 Key (如 X2, K1, X1)，若不指定则从环境变量读取
        """
        # 加载环境变量
        env_paths = [
            Path(__file__).parent.parent / '.env',
            Path.home() / '.env.jira'
        ]
        for p in env_paths:
            if p.exists():
                load_dotenv(p)
                break

        self.jira_url = os.getenv('JIRA_URL', 'https://jira.tap4fun.com/').rstrip('/')
        self.jira_token = os.getenv('JIRA_PERSONAL_TOKEN')

        # 支持动态指定项目 (默认 NK)
        self.project = project or os.getenv('JIRA_PROJECT', 'NK')

        if not self.jira_token:
            raise ValueError("缺少 JIRA_PERSONAL_TOKEN")

        self.jira = Jira(url=self.jira_url, token=self.jira_token)

        # 用于 REST API 直接调用
        self.headers = {
            "Authorization": f"Bearer {self.jira_token}",
            "Content-Type": "application/json",
        }

        # 加载项目配置
        self._load_project_config()

    def _load_project_config(self):
        """加载项目特定配置"""
        from lib.config import PROJECT_CONFIGS

        project_config = PROJECT_CONFIGS.get(self.project, {})

        # 部门 Leader - 优先从环境变量读取
        self.leaders = {}
        config_leaders = project_config.get('leaders', {})
        env_mappings = {
            '策划': f'LEADER_PLANNER_{self.project}',
            '客户端': f'LEADER_CLIENT_{self.project}',
            '服务器': f'LEADER_SERVER_{self.project}',
            '运营': f'LEADER_OPERATION_{self.project}',
            '测试': f'DEFAULT_TEST_ASSIGNEE_{self.project}',
        }
        for dept, env_key in env_mappings.items():
            self.leaders[dept] = os.getenv(env_key) or config_leaders.get(dept) or ''

        # 默认归属功能
        self.default_related_function = (
            os.getenv(f'DEFAULT_RELATED_FUNCTION_{self.project}') or
            project_config.get('default_related_function') or
            ''
        )

        # GitLab 项目路径
        self.gitlab_project = (
            project_config.get('gitlab_project') or
            os.getenv(f'GITLAB_PROJECT_{self.project}') or
            GITLAB_PROJECT
        )

        # Jira 字段 ID (项目特定)
        fields_config = project_config.get('fields', {})
        self.field_bug_level = fields_config.get('bug_level', 'customfield_10205')
        self.field_related_function = fields_config.get('related_function')  # 可能为 None
        self.field_reproduce_rate = fields_config.get('reproduce_rate', 'customfield_10028')
        self.field_expected_result = fields_config.get('expected_result', 'customfield_10206')
        self.field_actual_result = fields_config.get('actual_result', 'customfield_10207')

        # Bug 等级选项 ID (项目特定)
        self.bug_level_ids = project_config.get('bug_level_ids', BUG_LEVEL_IDS)

        # 复现步骤字段
        self.field_reproduce_steps = fields_config.get('reproduce_steps')

        # 必填字段和默认值
        self.required_fields = project_config.get('required_fields', [])
        self.use_feature_as_label = project_config.get('use_feature_as_label', False)

        # 功能负责人映射表
        self.feature_owners = project_config.get('feature_owners', {})

        print(f"  [项目] {self.project}")

    def _dept_to_env_key(self, dept: str) -> str:
        """部门名转环境变量 key"""
        mapping = {
            '策划': 'PLANNER',
            '客户端': 'CLIENT',
            '服务器': 'SERVER',
            '运营': 'OPERATION',
            '测试': 'TEST_ASSIGNEE',
        }
        return mapping.get(dept, dept.upper())

    def analyze_department(self, summary: str, description: str = '') -> str:
        """
        分析 Bug 描述，自动判断应分给哪个部门

        Returns:
            部门名称：UI, UX, GUI, 策划, 客户端, 服务器
        """
        text = f"{summary} {description}".lower()

        scores = {}
        for dept, keywords in DEPT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[dept] = score

        if not scores:
            # 默认策划
            return '策划'

        # 返回得分最高的部门
        return max(scores, key=scores.get)

    def analyze_bug_level(self, summary: str, description: str = '') -> str:
        """
        分析 Bug 描述，自动判断严重等级

        Returns:
            等级：A, B, C, D
        """
        text = f"{summary} {description}".lower()

        # A级：卡住、崩溃、无法进行、数据丢失、核心功能不可用
        a_keywords = [
            '卡住', '卡死', '死循环', '无限', '崩溃', 'crash', '闪退',
            '无法进入', '无法打开', '无法进行', '无法继续', '进不去', '打不开',
            '数据丢失', '数据错误', '存档丢失', '回档',
            '黑屏', '白屏', '无响应', '卡顿严重',
            '新手引导', '引导卡住', '强制引导',
            '无法登录', '登录失败', '掉线', '断线',
            '充值失败', '支付失败', '订单', '扣款',
        ]

        # B级：功能异常但有绕过方式、明显体验问题
        b_keywords = [
            '功能异常', '功能失效', '功能无效', '功能不正常',
            '无效', '不生效', '失效',
            '无法点击', '点击无效', '按钮无效', '点击无反应',
            '无法领取', '领取失败', '领取无效',
            '无法完成', '完成不了', '无法关闭',
            '显示错误', '数据显示错误', '数值错误',
            '奖励错误', '奖励异常', '领取失败',
            '红点', '不消失', '红点不消失', '红点异常',
            '动画异常', '特效异常', '音效异常',
            '重复', '刷新异常', '刷新失败',
            '进度未增加', '进度不增加', '进度没增加',
            '任务未完成', '任务完成不了', '不计数', '未计数',
            '界面挂了', '显示错乱', '无法正常使用', '模块无法使用',
        ]

        # D级：建议优化、美观问题
        d_keywords = [
            '建议', '优化', '希望', '可以考虑',
            '美观', '样式', '风格',
            '需求', '【需求】',
        ]

        # 检查 A 级
        for kw in a_keywords:
            if kw in text:
                return 'A'

        # 检查 B 级
        for kw in b_keywords:
            if kw in text:
                return 'B'

        # 检查 D 级
        for kw in d_keywords:
            if kw in text:
                return 'D'

        # 默认 C 级（显示问题、文案错误、小瑕疵）
        return 'C'

    def get_requirement_owners(self, issue_key: str) -> Dict[str, str]:
        """
        从需求单获取各岗位负责人

        Returns:
            {'UI': 'username', '策划': 'username', ...}
        """
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
            params = {"fields": ",".join(ROLE_FIELDS.values())}

            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()

            issue = resp.json()
            fields = issue.get("fields", {})

            owners = {}
            for role, field_id in ROLE_FIELDS.items():
                user_field = fields.get(field_id)
                if user_field and isinstance(user_field, dict):
                    # 获取 name (用户名) 而不是 displayName
                    owners[role] = user_field.get("name", "")

            return owners
        except Exception as e:
            print(f"  [获取需求负责人失败] {issue_key}: {e}")
            return {}

    def find_requirement_by_feature(self, feature: str) -> Optional[str]:
        """
        根据功能名搜索需求单

        Returns:
            需求单 key，如 X2-12345
        """
        try:
            jql = f'project = {self.project} AND summary ~ "{feature}" AND type in (需求, Story) ORDER BY created DESC'
            results = self.jira.jql(jql, limit=5)

            if results.get('issues'):
                return results['issues'][0]['key']
            return None
        except Exception as e:
            print(f"  [搜索需求失败] {feature}: {e}")
            return None

    def find_assignee(self, feature: str, department: str, summary: str = '', description: str = '') -> Tuple[str, str]:
        """
        智能查找负责人

        流程:
        1. 自动分析部门 (如果未指定)
        2. 查 feature-owner-map 映射表（优先）
        3. 查本地缓存
        4. 搜索 Jira 需求单
        5. 部门 Leader

        Returns:
            (assignee_username, department)
        """
        # 1. 自动分析部门
        if not department or department == 'auto':
            department = self.analyze_department(summary, description)
            print(f"  [自动分析部门] → {department}")

        # 2. 查 feature-owner-map 映射表（优先）
        if feature and OWNER_LOOKUP_AVAILABLE:
            try:
                owner_lookup = OwnerLookup()
                result, source = owner_lookup.lookup(feature)
                if result:
                    assignee = result.get(department)
                    if assignee:
                        print(f"  [映射表-{source}] {feature} / {department} → {assignee}")
                        return assignee, department

            except Exception as e:
                print(f"  [映射表查询失败] {e}")

        # 3. 搜索 Jira 需求单
        if feature:
            req_key = self.find_requirement_by_feature(feature)
            if req_key:
                print(f"  [找到需求] {req_key}")
                owners = self.get_requirement_owners(req_key)

                if owners:
                    # 返回目标部门的负责人
                    assignee = owners.get(department)
                    if assignee:
                        print(f"  [需求单负责人] {department} → {assignee}")
                        return assignee, department


        # 5. 查项目功能负责人映射表
        if feature and self.feature_owners:
            # 精确匹配
            if feature in self.feature_owners:
                owners = self.feature_owners[feature]
                if department in owners and owners[department]:
                    print(f"  [功能映射] {feature} / {department} → {owners[department]}")
                    return owners[department], department

            # 模糊匹配
            for feat_name, owners in self.feature_owners.items():
                if feature in feat_name or feat_name in feature:
                    if department in owners and owners[department]:
                        print(f"  [功能映射-模糊] {feat_name} / {department} → {owners[department]}")
                        return owners[department], department

        # 6. 从历史 Bug 学习：查找同功能的历史 Bug 经办人
        if feature:
            history_assignee = self._find_assignee_from_history(feature, department)
            if history_assignee:
                print(f"  [历史学习] {feature} / {department} → {history_assignee}")
                return history_assignee, department

        # 7. 使用 Leader (从项目配置获取)
        leader = self.leaders.get(department, self.leaders.get('策划', ''))
        print(f"  [使用Leader] {department} → {leader}")
        return leader, department

    def _get_cache_path(self) -> Path:
        """获取本地缓存文件路径"""
        return Path(__file__).parent.parent / 'data' / f'assignee-cache-{self.project}.json'

    def _load_assignee_cache(self) -> Dict:
        """加载本地经办人缓存"""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_assignee_cache(self, feature: str, department: str, assignee: str):
        """保存经办人到本地缓存"""
        cache_path = self._get_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        cache = self._load_assignee_cache()
        if feature not in cache:
            cache[feature] = {}
        cache[feature][department] = assignee

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [缓存保存失败] {e}")

    def _find_assignee_from_history(self, feature: str, department: str) -> Optional[str]:
        """
        查找功能负责人

        优先级：
        1. 本地缓存（创建 Bug 时记录的经办人，不受 Jira 状态变更影响）
        2. Jira 历史 Bug（仅作为补充）
        """
        # 1. 查本地缓存
        cache = self._load_assignee_cache()
        if feature in cache:
            assignee = cache[feature].get(department)
            if assignee:
                print(f"  [本地缓存] {feature} / {department} → {assignee}")
                return assignee

        # 模糊匹配缓存
        for cached_feature, depts in cache.items():
            if feature in cached_feature or cached_feature in feature:
                assignee = depts.get(department)
                if assignee:
                    print(f"  [本地缓存-模糊] {cached_feature} / {department} → {assignee}")
                    return assignee

        # 2. 查 Jira 历史（仅查未完成的 Bug，避免验收后经办人变更）
        try:
            jql = f'project = {self.project} AND labels = "{feature}" AND status not in (已完成, Done, Closed, 已关闭) ORDER BY created DESC'
            url = f'{self.jira_url}/rest/api/2/search'
            data = {'jql': jql, 'maxResults': 5, 'fields': ['assignee', 'labels']}

            resp = requests.post(url, headers=self.headers, json=data)
            if not resp.ok:
                return None

            issues = resp.json().get('issues', [])

            # 获取部门 Leader 列表
            dept_leaders = set()
            for dept, leader in self.leaders.items():
                if dept != '测试' and leader:
                    dept_leaders.add(leader)

            for issue in issues:
                assignee = issue['fields'].get('assignee')
                if assignee:
                    assignee_name = assignee.get('name', '')
                    if assignee_name and assignee_name not in dept_leaders:
                        return assignee_name

            return None
        except Exception as e:
            print(f"  [历史学习失败] {e}")
            return None

    def find_test_issue(self, feature: str) -> Optional[str]:
        """搜索测试单（带 labels=测试 标签的单子）"""
        try:
            jql = f'project = {self.project} AND summary ~ "{feature}" AND labels = 测试 ORDER BY created DESC'
            url = f'{self.jira_url}/rest/api/2/search'
            data = {'jql': jql, 'maxResults': 5, 'fields': ['summary', 'labels']}

            resp = requests.post(url, headers=self.headers, json=data)
            if resp.ok:
                issues = resp.json().get('issues', [])
                if issues:
                    return issues[0].get('key')
        except Exception:
            pass
        return None

    def _lookup_test_key_from_cache(self, feature: str) -> str:
        """从 feature-owner-map 缓存中查找测试单 Key"""
        try:
            owner_map_path = Path(__file__).parent.parent.parent / 'feature-owner-map' / 'data' / 'owner-map.json'
            if not owner_map_path.exists():
                return ''
            with open(owner_map_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            features = cache.get('features', {})
            # 精确匹配
            if feature in features:
                return features[feature].get('test_key', '')
            # 模糊匹配
            for cached_feature, info in features.items():
                if feature in cached_feature or cached_feature in feature:
                    return info.get('test_key', '')
        except Exception:
            pass
        return ''

    def find_test_key(self, feature: str) -> str:
        """查找归属功能（测试单号）

        归属功能必须是带有 labels=测试 标签的测试单
        查找顺序：
        1. feature-owner-map 缓存中的 test_key
        2. Jira 搜索测试单（labels=测试）
        3. 默认值 X2-39092
        """
        if not feature:
            return DEFAULT_RELATED_FUNCTION

        # 1. 查 feature-owner-map 缓存
        test_key = self._lookup_test_key_from_cache(feature)
        if test_key:
            print(f"  [归属功能-缓存] {feature} → {test_key}")
            return test_key

        # 2. 搜索测试单（带 labels=测试 标签）
        test_key = self.find_test_issue(feature)
        if test_key:
            print(f"  [归属功能-测试单] {feature} → {test_key}")
            return test_key

        # 3. 使用默认值 (从项目配置获取)
        print(f"  [归属功能-默认] → {self.default_related_function}")
        return self.default_related_function

    def normalize_version(self, version: str) -> str:
        """标准化版本号"""
        if not version:
            return ''

        # 特殊版本：直接返回，不做标准化
        if version in ['线上版本', '下个版本']:
            return version

        # NK 等项目版本格式如 581(7.2)_dev，不做标准化
        if '(' in version or '_dev' in version or '_qa' in version:
            return version.strip()

        v = version.replace('版本', '').strip()
        if v and v[0] in 'vV':
            v = v[1:].strip()

        if v.isdigit():
            return f"0.{v}.0"

        parts = v.split('.')
        if len(parts) == 2:
            return f"{v}.0"

        return v

    # ========== 版本智能优先级相关方法 ==========

    def get_project_versions(self) -> List[Dict]:
        """获取项目所有版本"""
        try:
            url = f"{self.jira_url}/rest/api/2/project/{self.project}/versions"
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"  [获取项目版本失败] {e}")
            return []

    def get_version_from_issue(self, issue_key: str) -> str:
        """
        从指定 Issue 中获取修复版本号

        Args:
            issue_key: Issue Key

        Returns:
            版本号字符串，如 "0.25.0"；若未找到则返回空字符串
        """
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
            params = {"fields": "fixVersions"}

            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()

            issue = resp.json()
            fix_versions = issue.get("fields", {}).get("fixVersions", [])

            if fix_versions:
                # 取第一个修复版本
                version_name = fix_versions[0].get("name", "")
                normalized = self.normalize_version(version_name)
                if normalized:
                    print(f"  [从归属功能获取版本] {issue_key} → {normalized}")
                    return normalized
            return ''
        except Exception as e:
            print(f"  [获取归属功能版本失败] {issue_key}: {e}")
            return ''

    def get_issue_status(self, issue_key: str) -> str:
        """
        获取 Issue 的状态

        Args:
            issue_key: Issue Key

        Returns:
            状态名称，如 "已完成"、"进行中"等；失败返回空字符串
        """
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
            params = {"fields": "status"}

            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()

            issue = resp.json()
            status = issue.get("fields", {}).get("status", {})
            status_name = status.get("name", "")

            return status_name
        except Exception as e:
            print(f"  [获取归属功能状态失败] {issue_key}: {e}")
            return ""

    def get_online_version(self) -> str:
        """
        获取线上版本（已发布的最高版本）

        Returns:
            线上版本号，如 "0.24.0"；若无已发布版本则返回空字符串
        """
        versions = self.get_project_versions()
        if not versions:
            return ''

        # 筛选已发布的版本
        released = [v for v in versions if v.get('released') and valid_name(v)]

        if released:
            # 取已发布版本中最高的
            chosen = max(released, key=lambda v: valid_name(v))
            return self.normalize_version(valid_name(chosen))

        return ''

    def get_default_version(self, prefer_unreleased: bool = True, prefer_min: bool = False) -> str:
        """
        动态获取默认修复版本。

        策略：
        - prefer_min=True: 取「未发布」中版本名最小的（用于默认归属功能 X2-39092）
        - prefer_min=False: 取「未发布」中版本名最大的；若无未发布则取「已发布」中最大的
        """
        versions = self.get_project_versions()
        if not versions:
            return ''

        unreleased = [v for v in versions if not v.get('released') and valid_name(v)]
        released = [v for v in versions if v.get('released') and valid_name(v)]

        if unreleased:
            if prefer_min:
                chosen = min(unreleased, key=lambda v: valid_name(v))
                version = self.normalize_version(valid_name(chosen))
                print(f"  [动态版本-最低未发布] → {version}")
            else:
                chosen = max(unreleased, key=lambda v: valid_name(v))
                version = self.normalize_version(valid_name(chosen))
                print(f"  [动态版本-最高未发布] → {version}")
            return version
        elif released:
            chosen = max(released, key=lambda v: valid_name(v))
            version = self.normalize_version(valid_name(chosen))
            print(f"  [动态版本-最高已发布] → {version}")
            return version

        return ''

    def get_latest_unreleased_version(self) -> str:
        """获取最新的未发布版本（原始名称，不做标准化）"""
        versions = self.get_project_versions()
        if not versions:
            return ''

        # 筛选未发布版本，排除特殊名称
        skip_names = {'Cancelled', 'Backlog后续开发', '线上_qa'}
        unreleased = [
            v for v in versions
            if not v.get('released') and valid_name(v) and valid_name(v) not in skip_names
        ]

        if unreleased:
            # 按名称排序取最新的
            chosen = max(unreleased, key=lambda v: valid_name(v))
            return valid_name(chosen)

        return ''

    def get_lowest_unreleased_version(self) -> str:
        """获取未发布版本中最低的那个（用于修复版本）"""
        versions = self.get_project_versions()
        if not versions:
            return ''

        # 筛选未发布版本，排除特殊名称
        skip_names = {'Cancelled', 'Backlog后续开发', '线上_qa'}
        unreleased = [
            v for v in versions
            if not v.get('released') and valid_name(v) and valid_name(v) not in skip_names
        ]

        if unreleased:
            # 按名称排序取最低的
            chosen = min(unreleased, key=lambda v: valid_name(v))
            return valid_name(chosen)

        return ''

    def get_previous_version(self, current_version: str) -> str:
        """获取比当前版本低一个的版本（用于线上 bug 的影响版本）"""
        versions = self.get_project_versions()
        if not versions:
            return current_version

        # 筛选有效版本，排除特殊名称
        skip_names = {'Cancelled', 'Backlog后续开发', '线上_qa'}
        valid_versions = [
            v for v in versions
            if valid_name(v) and valid_name(v) not in skip_names
        ]

        # 按名称排序
        sorted_versions = sorted(valid_versions, key=lambda v: valid_name(v))
        version_names = [valid_name(v) for v in sorted_versions]

        # 找到当前版本的位置
        if current_version in version_names:
            idx = version_names.index(current_version)
            if idx > 0:
                return version_names[idx - 1]

        return current_version

    def query_gitlab_branches(self, issue_key: str) -> List[str]:
        """
        查询 GitLab 中包含指定 JIRA ID 的分支

        通过 GitLab Search API 搜索包含 JIRA ID 的 commits，
        获取这些 commits 所在的分支。

        Args:
            issue_key: JIRA Issue Key，如 X2-12345

        Returns:
            关键分支列表，如 ['master', 'dev']
        """
        try:
            # 获取 GitLab 项目 ID (使用项目配置)
            gitlab_project = getattr(self, 'gitlab_project', GITLAB_PROJECT)
            project_encoded = gitlab_project.replace('/', '%2F')

            # 通过 Search API 搜索包含 JIRA ID 的 commits
            search_url = f"{GITLAB_URL}/api/v4/projects/{project_encoded}/search"
            params = {
                'scope': 'commits',
                'search': issue_key,
                'per_page': 5
            }
            gitlab_headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}

            resp = requests.get(search_url, headers=gitlab_headers, params=params, timeout=5)
            if not resp.ok:
                return []

            commits = resp.json()
            if not commits:
                return []

            # 获取这些 commits 所在的分支
            all_branches = set()
            key_branches = set(BRANCH_VERSION_MAPPING['online'] + BRANCH_VERSION_MAPPING['development'])

            for commit in commits[:5]:
                commit_sha = commit.get('id', '')
                if not commit_sha:
                    continue

                # 查询 commit 所在的分支
                refs_url = f"{GITLAB_URL}/api/v4/projects/{project_encoded}/repository/commits/{commit_sha}/refs"
                try:
                    refs_resp = requests.get(refs_url, headers=gitlab_headers, timeout=5)
                    if refs_resp.ok:
                        refs = refs_resp.json()
                        for ref in refs:
                            if ref.get('type') == 'branch':
                                branch_name = ref.get('name', '')
                                # 只关注关键分支
                                if branch_name in key_branches:
                                    all_branches.add(branch_name)
                except Exception:
                    continue

            return list(all_branches)
        except Exception as e:
            print(f"  [GitLab查询失败] {issue_key}: {e}")
            return []

    def determine_version_by_branches(self, branches: List[str], issue_key: str) -> Optional[str]:
        """
        根据分支列表判断修复版本

        Args:
            branches: 分支名列表
            issue_key: JIRA Issue Key

        Returns:
            版本号字符串，或 None（需要 fallback）
        """
        # 检查是否在线上分支
        online_branches = set(branches) & set(BRANCH_VERSION_MAPPING['online'])
        if online_branches:
            print(f"  [分支判断] {issue_key} 在线上分支 {list(online_branches)} → 线上版本")
            return "线上版本"

        # 检查是否仅在开发分支
        dev_branches = set(branches) & set(BRANCH_VERSION_MAPPING['development'])
        if dev_branches:
            print(f"  [分支判断] {issue_key} 仅在开发分支 {list(dev_branches)}")
            return self.get_version_from_issue(issue_key)

        return None

    # ========== 客诉单媒体转存 ==========

    # 可直接下载的媒体域名白名单。只从这些已知的自家 CDN 拉取，
    # 避免把描述里随手贴的任意外链也下载上传。
    MEDIA_HOST_WHITELIST = (
        'pf-chat-cn2cn-a.tap4fun.com',
        'pf-chat-cn2cn-b.tap4fun.com',
        'pf-chat.tap4fun.com',
    )

    # 明确不是媒体、只是后台入口的链接，直接跳过
    MEDIA_HOST_BLACKLIST = (
        'igame.tap4fun.com',
        'jira.tap4fun.com',
        'wiki.tap4fun.com',
    )

    MEDIA_MIME_EXT = {
        'video/mp4': '.mp4',
        'video/quicktime': '.mov',
        'video/webm': '.webm',
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/gif': '.gif',
        'image/webp': '.webp',
    }

    # 单个文件大小上限，防止把超大录屏怼进 Jira（Jira 默认单附件限制通常为 10-25MB，
    # 这里放宽到 60MB 由服务端最终裁决，只拦明显异常的体积）
    MEDIA_MAX_BYTES = 60 * 1024 * 1024

    # 客诉单号形态。默认只认 CS（客服工单项目）；如需扩展别的项目前缀，
    # 加到这里即可。用 (?<![A-Za-z0-9]) 而非 \b，避免把 "XCS-123" 也当成 CS 单。
    CS_KEY_PATTERN = re.compile(r'(?<![A-Za-z0-9])(CS-\d{3,})(?![0-9])', re.IGNORECASE)

    @classmethod
    def detect_cs_keys(cls, *texts: str) -> List[str]:
        """
        从任意文本里识别客诉单号，按出现顺序去重返回。

        能同时认出裸单号（CS-299536）和 Jira 链接里的单号
        （https://jira.tap4fun.com/browse/CS-299536）。
        """
        found, seen = [], set()
        for t in texts:
            if not t:
                continue
            for mt in cls.CS_KEY_PATTERN.finditer(t):
                key = mt.group(1).upper()
                if key not in seen:
                    seen.add(key)
                    found.append(key)
        return found

    def collect_media_from_issue(self, source_key: str,
                                 max_files: int = 10) -> List[Dict[str, Any]]:
        """
        从客诉单（CS-xxx）收集媒体，返回本地文件描述列表。

        两个来源：
        1. 该单的 Jira 原生附件 —— 需带 PAT 下载
        2. 描述与评论正文里的媒体直链（如 pf-chat CDN 上的录屏）—— 匿名可下

        返回 [{'path': ..., 'filename': ..., 'size': ..., 'origin': ...}, ...]
        失败的条目带 'error' 字段，交由调用方决定是否提示。
        """
        import tempfile
        from urllib.parse import urlparse, unquote

        headers = {
            'Authorization': f'Bearer {self.jira_token}',
            'Accept': 'application/json',
        }
        collected: List[Dict[str, Any]] = []
        tmpdir = Path(tempfile.gettempdir()) / f'jira_media_{source_key}'
        tmpdir.mkdir(parents=True, exist_ok=True)

        def _download(link: str, with_auth: bool, origin: str,
                      prefer_name: str = '') -> Optional[Dict[str, Any]]:
            try:
                resp = requests.get(
                    link,
                    headers=headers if with_auth else None,
                    timeout=120,
                    stream=True,
                    allow_redirects=True,
                )
            except Exception as e:
                return {'origin': origin, 'url': link,
                        'error': f'{type(e).__name__}: {e}'}

            if resp.status_code != 200:
                resp.close()
                return {'origin': origin, 'url': link,
                        'error': f'HTTP {resp.status_code}'}

            ctype = (resp.headers.get('Content-Type') or '').split(';')[0].strip()
            clen = resp.headers.get('Content-Length')
            if clen and int(clen) > self.MEDIA_MAX_BYTES:
                resp.close()
                return {'origin': origin, 'url': link,
                        'error': f'文件过大 {int(clen) / 1048576:.1f}MB，跳过'}

            # 非视频/图片一律不要（避免把 HTML 错误页当成媒体存下来）
            if not (ctype.startswith('video/') or ctype.startswith('image/')):
                resp.close()
                return {'origin': origin, 'url': link,
                        'error': f'非媒体类型 {ctype or "unknown"}，跳过'}

            name = prefer_name or unquote(Path(urlparse(link).path).name) or 'media'
            # CDN 上的录屏文件名多是无意义 UUID，换成能看懂的名字
            # （如 CS-299536_玩家录屏_1.mp4），开发在附件列表里一眼能认出来源
            if not prefer_name:
                stem = Path(name).stem
                looks_like_uuid = (len(stem) >= 32
                                   and re.fullmatch(r'[0-9a-fA-F-]+', stem) is not None)
                if looks_like_uuid or not stem:
                    kind = '玩家录屏' if ctype.startswith('video/') else '玩家截图'
                    idx = sum(1 for c in collected if 'path' in c) + 1
                    name = f'{source_key}_{kind}_{idx}'
            if not Path(name).suffix:
                name += self.MEDIA_MIME_EXT.get(ctype, '.bin')

            dest = tmpdir / name
            n = 1
            while dest.exists():
                dest = tmpdir / f'{Path(name).stem}_{n}{Path(name).suffix}'
                n += 1

            written = 0
            try:
                with open(dest, 'wb') as fh:
                    for chunk in resp.iter_content(256 * 1024):
                        if not chunk:
                            continue
                        written += len(chunk)
                        if written > self.MEDIA_MAX_BYTES:
                            raise ValueError('下载中超出大小上限')
                        fh.write(chunk)
            except Exception as e:
                resp.close()
                dest.unlink(missing_ok=True)
                return {'origin': origin, 'url': link,
                        'error': f'写入失败: {e}'}
            resp.close()

            return {'path': str(dest), 'filename': dest.name,
                    'size': written, 'origin': origin, 'url': link}

        # --- 来源1: 原生附件 ---
        try:
            r = requests.get(f"{self.jira_url}/rest/api/2/issue/{source_key}",
                             headers=headers, timeout=30)
            if r.status_code != 200:
                print(f"  [媒体] 读取 {source_key} 失败 HTTP {r.status_code}")
                return collected
            issue = r.json()
        except Exception as e:
            print(f"  [媒体] 读取 {source_key} 异常: {e}")
            return collected

        fields = issue.get('fields', {})
        for a in (fields.get('attachment') or []):
            if len(collected) >= max_files:
                break
            mime = (a.get('mimeType') or '')
            if not (mime.startswith('video/') or mime.startswith('image/')):
                continue
            got = _download(a['content'], with_auth=True,
                            origin=f'{source_key} 附件',
                            prefer_name=a.get('filename', ''))
            if got:
                collected.append(got)

        # --- 来源2: 正文与评论里的媒体直链 ---
        texts = [fields.get('description') or '']
        try:
            cm = requests.get(
                f"{self.jira_url}/rest/api/2/issue/{source_key}/comment",
                headers=headers, timeout=30)
            if cm.status_code == 200:
                for c in cm.json().get('comments', []):
                    texts.append(c.get('body') or '')
        except Exception:
            pass

        seen_urls = set()
        for t in texts:
            for link in re.findall(r'https?://[^\s\)\]\}，,；;"\'）]+', t):
                link = link.rstrip('.,;:）)')
                if link in seen_urls:
                    continue
                seen_urls.add(link)
                host = urlparse(link).netloc.lower()
                if any(b in host for b in self.MEDIA_HOST_BLACKLIST):
                    continue
                if not any(w in host for w in self.MEDIA_HOST_WHITELIST):
                    continue
                if len(collected) >= max_files:
                    break
                got = _download(link, with_auth=False,
                                origin=f'{source_key} 正文链接')
                if got:
                    collected.append(got)

        ok = [c for c in collected if 'path' in c]
        bad = [c for c in collected if 'error' in c]
        if ok:
            total = sum(c['size'] for c in ok) / 1048576
            print(f"  [媒体] 从 {source_key} 取到 {len(ok)} 个文件"
                  f"（合计 {total:.1f}MB）")
            for c in ok:
                print(f"         {c['filename']} "
                      f"{c['size'] / 1048576:.1f}MB ← {c['origin']}")
        for c in bad:
            print(f"  [媒体] 跳过 {c['url'][:80]}: {c['error']}")
        if not ok and not bad:
            print(f"  [媒体] {source_key} 未发现可转存的图片/视频")

        return collected

    # ========== 建单后核对兜底 ==========

    # 需要核对的字段：字段 key -> 显示名
    # 只覆盖"显式传入、且实测可能被自动推断或工作流改写"的字段。
    # labels / versions 等 Jira 侧本就会规范化的字段不纳入，避免噪音告警。
    VERIFY_FIELD_LABELS = {
        'assignee': '经办人',
        'fixVersions': '修复版本',
        'versions': '影响版本',
        'customfield_10028': '重现概率',
    }

    @staticmethod
    def _field_identity(raw):
        """
        把 Jira 字段值归一成"标识符集合的列表"，用于宽松比较。

        同一个选项在提交侧和读回侧可能用不同 key 表示：提交
        {'id': '10010'} 而 Jira 返回 {'value': 'Always', 'id': '10010'}。
        因此收集全部候选标识符，只要两侧有交集就算一致。
        """
        def ident(x):
            if x is None:
                return None
            if isinstance(x, dict):
                vals = {str(x[k]) for k in ('name', 'value', 'id') if x.get(k)}
                return vals or None
            return {str(x)}

        if raw is None:
            return None
        if isinstance(raw, list):
            out = [ident(x) for x in raw]
            return [v for v in out if v]
        one = ident(raw)
        return [one] if one else None

    @classmethod
    def _values_match(cls, want_raw, got_raw) -> bool:
        """两侧字段值是否等价（按标识符交集判断，忽略 name/value/id 表示差异）"""
        want = cls._field_identity(want_raw)
        got = cls._field_identity(got_raw)
        if not want:
            return True  # 没提交这个字段，无需比较
        if not got or len(want) != len(got):
            return False
        # 逐项要求存在交集；顺序不同的多值字段按集合匹配
        remaining = list(got)
        for w in want:
            hit = next((g for g in remaining if w & g), None)
            if hit is None:
                return False
            remaining.remove(hit)
        return True

    @staticmethod
    def _display_value(raw):
        """取一个人类可读的展示值，仅用于日志"""
        idents = SmartBugCreator._field_identity(raw)
        if not idents:
            return None
        shown = []
        for s in idents:
            # 优先展示非纯数字的那个（'Always' 而不是 '10010'）
            pretty = sorted(s, key=lambda v: (v.isdigit(), v))
            shown.append(pretty[0])
        return shown[0] if len(shown) == 1 else shown

    def _verify_and_backfill(self, key: str, submitted: Dict[str, Any]) -> Dict[str, Any]:
        """
        建单后读回关键字段，与提交值不一致时自动 PUT 补写。

        存在的原因：Jira 侧的必填校验、工作流后处理、以及本脚本自身的
        关键词自动推断，都可能让最终落库的值与提交值不同（例如重现概率
        被描述里的"一次"字样误判）。静默不一致比报错更难发现，所以这里
        统一读回核对。
        """
        checks = {k: v for k, v in self.VERIFY_FIELD_LABELS.items() if k in submitted}
        if not checks:
            return {'checked': [], 'fixed': [], 'failed': []}

        headers = {
            'Authorization': f'Bearer {self.jira_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        try:
            resp = requests.get(
                f"{self.jira_url}/rest/api/2/issue/{key}",
                headers=headers,
                params={'fields': ','.join(checks)},
                timeout=30,
            )
            if resp.status_code != 200:
                print(f"  [核对] 读回失败 HTTP {resp.status_code}，跳过核对")
                return {'checked': [], 'fixed': [], 'failed': [],
                        'error': f'HTTP {resp.status_code}'}
            actual_fields = resp.json().get('fields', {})
        except Exception as e:
            print(f"  [核对] 读回异常，跳过核对: {e}")
            return {'checked': [], 'fixed': [], 'failed': [], 'error': str(e)}

        mismatched, fixed, failed = {}, [], []
        for fkey, label in checks.items():
            want_raw = submitted.get(fkey)
            got_raw = actual_fields.get(fkey)
            if want_raw is None:
                continue
            if not self._values_match(want_raw, got_raw):
                mismatched[fkey] = want_raw
                print(f"  [核对] {label} 不一致: 提交 {self._display_value(want_raw)!r} "
                      f"→ 实际 {self._display_value(got_raw)!r}，尝试补写")

        if not mismatched:
            print(f"  [核对] {len(checks)} 个关键字段全部一致")
            return {'checked': list(checks), 'fixed': [], 'failed': []}

        # 逐字段补写，避免一个字段被 Jira 拒绝导致整批失败
        for fkey, value in mismatched.items():
            label = checks[fkey]
            try:
                r = requests.put(
                    f"{self.jira_url}/rest/api/2/issue/{key}",
                    headers=headers,
                    data=json.dumps({'fields': {fkey: value}}),
                    timeout=30,
                )
                if r.status_code in (200, 204):
                    fixed.append(label)
                    print(f"  [核对] 已修正: {label}")
                else:
                    failed.append(label)
                    print(f"  [核对] 修正失败 {label}: HTTP {r.status_code} {r.text[:200]}")
            except Exception as e:
                failed.append(label)
                print(f"  [核对] 修正异常 {label}: {e}")

        return {'checked': list(checks), 'fixed': fixed, 'failed': failed}

    def create_bug(
        self,
        summary: str,
        feature: str = '',
        department: str = 'auto',  # 默认自动分析
        bug_level: str = 'auto',   # 默认自动分析
        version: str = '',
        description: str = '',
        expected: str = '',        # 预期结果
        actual: str = '',          # 实际结果
        assignee: str = '',
        related_function: str = '',
        attachment='',  # 本地附件路径，单个字符串或路径列表
        is_online_bug: bool = False,  # 是否是线上 bug
        feedback_source: str = '',  # 反馈来源：客服反馈/QA反馈/项目组反馈
        reproduce_rate: str = '',  # 重现概率 Always/High/Medium/Low/Once，留空则按关键词自动识别
        verify: bool = True,  # 建单后读回关键字段核对，不一致则自动补写
        media_from_issue: str = '',  # 客诉单号（如 CS-299536）；留空则自动从描述/预期/实际里识别
        auto_media: bool = True,  # 未显式指定时，是否自动识别描述里的客诉单号并转存媒体
        affect_version: str = '',  # 影响版本；留空则线上bug取修复版本的上一个、否则同修复版本
    ) -> Dict[str, Any]:
        """创建 Bug"""

        print(f"\n创建 Bug: {summary}")
        if feature:
            print(f"功能: {feature}")

        # 用于关键词识别的原始文本
        text = f"{summary} {description}"

        # 清理概述中的指定信息（这些不应该出现在 Bug 标题中）
        clean_summary = summary
        remove_keywords = [
            # 线上标记
            '线上问题', '线上', '正式服', '外网', '生产环境',
            # 反馈来源
            '客服反馈', 'QA反馈', '项目组反馈', '客服', '项目组',
            # 重现概率
            '偶现高', '偶现中', '偶现低', '一次', '高概率', '中概率', '低概率', '仅一次',
            # 优先级
            '优先级非常高', '优先级最低', '优先级一般', '优先级高', '优先级低',
            '非常高优先', '最低优先', '一般优先', '高优先', '低优先', '普通优先',
        ]
        for kw in remove_keywords:
            clean_summary = clean_summary.replace(kw, '')
        # 清理多余的标点和空格
        clean_summary = clean_summary.replace('，，', '，').replace('、、', '、').replace('  ', ' ')
        clean_summary = clean_summary.strip('，、, ')
        summary = clean_summary

        # 自动识别线上 bug（关键词）- 使用原始 text
        online_keywords = ['线上', '正式服', '外网', '生产环境']
        if not is_online_bug:
            if any(kw in text for kw in online_keywords):
                is_online_bug = True
                print(f"  [识别为线上Bug]")

        # 自动识别反馈来源
        if is_online_bug and not feedback_source:
            if '客服反馈' in text or '客服' in text:
                feedback_source = '客服反馈'
            elif 'QA反馈' in text or 'QA' in text:
                feedback_source = 'QA反馈'
            elif '项目组反馈' in text or '项目组' in text:
                feedback_source = '项目组反馈'
            if feedback_source:
                print(f"  [反馈来源] {feedback_source}")

        # 重现概率
        # 优先使用调用方显式传入的值；未传入时才按关键词自动识别
        if reproduce_rate:
            if reproduce_rate not in REPRODUCE_RATE_IDS:
                print(f"  [重现概率] 传入值 {reproduce_rate!r} 无效，"
                      f"可选: {'/'.join(REPRODUCE_RATE_IDS)}，回退为 Always")
                reproduce_rate = 'Always'
            else:
                print(f"  [重现概率] {reproduce_rate} (显式指定)")
        else:
            # 自动识别：默认必现，根据关键词识别其他概率
            # 注意关键词必须足够特异 —— "一次"/"偶现" 这类词在正常叙述中极常见
            # （如"必须先落过一次值"），只匹配裸词会误判，因此统一要求带上下文限定
            if '偶现高' in text or '高概率' in text:
                reproduce_rate = 'High'
                print(f"  [重现概率] 偶现高")
            elif '偶现中' in text or '中概率' in text:
                reproduce_rate = 'Medium'
                print(f"  [重现概率] 偶现中")
            elif '偶现低' in text or '低概率' in text or '偶现' in text:
                reproduce_rate = 'Low'
                print(f"  [重现概率] 偶现低")
            elif ('仅一次' in text or '仅出现一次' in text or '只出现一次' in text
                  or '重现概率：一次' in text or '重现概率:一次' in text):
                reproduce_rate = 'Once'
                print(f"  [重现概率] 一次")
            else:
                reproduce_rate = 'Always'
                print(f"  [重现概率] Always (默认)")

        # 自动识别优先级
        # 默认非常高，根据关键词识别其他优先级
        if '优先级最低' in text or '最低优先' in text:
            priority = '最低'
            print(f"  [优先级] 最低")
        elif '优先级低' in text or '低优先' in text:
            priority = '低'
            print(f"  [优先级] 低")
        elif '优先级一般' in text or '一般优先' in text or '普通优先' in text:
            priority = '一般'
            print(f"  [优先级] 一般")
        elif '优先级高' in text or '高优先' in text:
            priority = '高'
            print(f"  [优先级] 高")
        else:
            priority = '非常高'  # 默认非常高

        # 生成完整概要 (智能提取核心功能名)；若 summary 已含【】则不再重复添加
        core_feature = extract_core_feature_name(feature) if feature else ''
        if core_feature and not summary.strip().startswith('【'):
            full_summary = f"【{core_feature}】{summary}"
        else:
            full_summary = summary

        # 特殊规则检测
        is_firebase = is_firebase_crash(description, summary)
        is_merge_server = any(kw in feature.lower() for kw in ['合服', '合服后']) if feature else False

        # 自动分析 Bug 等级 (考虑 Firebase 特殊规则)
        if bug_level == 'auto':
            if is_firebase:
                bug_level = 'C'  # Firebase 报错默认 C 级
                print(f"  [Firebase报错] 默认等级 → {bug_level}")
            else:
                bug_level = self.analyze_bug_level(summary, description)
                print(f"  [自动判断等级] → {bug_level}")

        # 确定经办人和部门 (考虑 Firebase 特殊规则)
        if not assignee:
            # Firebase 报错自动分配给客户端
            if is_firebase and department == 'auto':
                department = '客户端'
                print(f"  [Firebase报错] 自动分配部门 → {department}")
            assignee, department = self.find_assignee(feature, department, summary, description)

        # 归属功能（需要在版本判断之前确定）
        if not related_function:
            # 特殊规则优先: Firebase报错/合服 → 直接使用常规功能
            if feature and feature in SPECIAL_FEATURE_RULES:
                related_function = self.default_related_function
                print(f"  [特殊规则] {feature} → {related_function}")
            elif is_firebase:
                related_function = self.default_related_function
                print(f"  [Firebase报错] 归属功能 → {related_function}")
            elif is_merge_server:
                related_function = self.default_related_function
                print(f"  [合服相关] 归属功能 → {related_function}")
            else:
                related_function = self.find_test_key(feature) if feature else DEFAULT_RELATED_FUNCTION

        # ========== 版本号智能优先级 ==========
        # 优先级 1: 显式指定
        version = self.normalize_version(version) if version else ''

        # 如果项目有归属功能字段，走智能版本获取
        if not version and self.field_related_function and related_function:
            # 优先级 2: 从归属功能获取版本
            version_from_feature = self.get_version_from_issue(related_function)
            if version_from_feature:
                version = version_from_feature

            if not version:
                # 优先级 3: 通过 Git 分支判断版本
                print(f"  [查询分支] 正在查询 {related_function} 所在分支...")
                branches = self.query_gitlab_branches(related_function)
                if branches:
                    print(f"  [找到分支] {', '.join(branches)}")
                    version_from_branch = self.determine_version_by_branches(branches, related_function)
                    if version_from_branch:
                        version = version_from_branch
                else:
                    print(f"  [未找到分支] {related_function}")

            if not version:
                # 优先级 4: 动态获取（根据归属功能类型）
                is_default_function = (related_function == self.default_related_function)
                version = self.get_default_version(prefer_min=is_default_function)

        # 如果项目没有归属功能字段但需要版本（如 NK），获取未发布版本中最低的
        if not version and 'fixVersions' in self.required_fields:
            version = self.get_lowest_unreleased_version()
            if version:
                print(f"  [修复版本] → {version}")

        # 计算影响版本
        if version:
            if affect_version:
                # 调用方显式指定，优先采用（如线上问题挂到 "线上_qa"）
                print(f"  [影响版本] {affect_version} (显式指定)")
            elif is_online_bug:
                # 线上 bug：影响版本 = 修复版本的上一个版本
                affect_version = self.get_previous_version(version)
                print(f"  [线上Bug] 影响版本 → {affect_version}")
            else:
                # 测试版本 bug：影响版本 = 修复版本
                affect_version = version
        else:
            affect_version = affect_version or ''

        # ========== 构建字段 ==========
        fields = {
            'project': {'key': self.project},
            'summary': full_summary,
            'issuetype': {'id': '10004'},  # Bug
            'assignee': {'name': assignee},
            'priority': {'name': priority},
        }

        # 重现概率
        if self.field_reproduce_rate:
            fields[self.field_reproduce_rate] = {'id': REPRODUCE_RATE_IDS.get(reproduce_rate, REPRODUCE_RATE_IDS['Always'])}

        # Bug 等级
        if self.field_bug_level:
            fields[self.field_bug_level] = {'id': self.bug_level_ids.get(bug_level, self.bug_level_ids.get('B', '10105'))}

        # 预期结果
        if self.field_expected_result:
            fields[self.field_expected_result] = expected or '正常显示/功能正常'

        # 实际结果
        if self.field_actual_result:
            fields[self.field_actual_result] = actual or description or summary

        # 归属功能 (有些项目没有这个字段)
        if self.field_related_function and related_function:
            fields[self.field_related_function] = related_function

        # 复现步骤 (NK 项目必填)
        # 优先使用调用方传入的 description；没有时再退化到 summary 拼接
        if self.field_reproduce_steps:
            if description and description.strip():
                reproduce_steps = description.strip()
            else:
                reproduce_steps = f"1. 进入{feature or '相关'}界面\n2. {summary}"
            fields[self.field_reproduce_steps] = reproduce_steps

        # 标签 (NK 项目使用功能名作为标签)
        if self.use_feature_as_label and feature:
            labels = [feature]
            # 线上 bug 需要添加反馈来源标签
            if is_online_bug and feedback_source:
                labels.append(feedback_source)
            fields['labels'] = labels

        # 版本
        if version:
            fields['fixVersions'] = [{'name': version}]
            # 影响版本
            if 'versions' in self.required_fields and affect_version:
                fields['versions'] = [{'name': affect_version}]

        try:
            result = self.jira.create_issue(fields=fields)
            key = result['key']

            # 保存经办人到本地缓存（不受 Jira 验收流转影响）
            if feature and assignee:
                self._save_assignee_cache(feature, department, assignee)

            # 上传附件
            # 支持三种来源：显式传入的本地路径（单个或列表）、
            # 以及从客诉单转存下来的图片/视频
            attachment_result = None
            uploaded, upload_failed = [], []

            pending: List[Dict[str, Any]] = []
            if attachment:
                paths = attachment if isinstance(attachment, (list, tuple)) else [attachment]
                for p in paths:
                    if p and Path(p).exists():
                        pending.append({'path': str(p), 'filename': Path(p).name,
                                        'origin': '本地文件'})
                    elif p:
                        upload_failed.append(f'{p}(文件不存在)')

            # 客诉单媒体：显式指定优先；未指定时按 auto_media 从正文识别 CS 单号
            # 注意：调用方已显式给了 attachment 时不再自动抓取——否则描述里提到的
            # 客诉单号会把该单全部媒体又拉一遍，和手工挑好的附件重复。
            media_keys: List[str] = []
            if media_from_issue:
                media_keys = [k.strip().upper() for k in
                              (media_from_issue if isinstance(media_from_issue, (list, tuple))
                               else [media_from_issue]) if k and k.strip()]
            elif auto_media and not pending:
                media_keys = self.detect_cs_keys(description, expected, actual, summary)
                if media_keys:
                    print(f"  [媒体] 从描述识别到客诉单: {', '.join(media_keys)}")
            elif auto_media and pending:
                print(f"  [媒体] 已显式指定 {len(pending)} 个附件，跳过自动转存")

            # 已在待上传列表里的文件名（去掉重名去重后缀）用于跳过重复
            def _base(n: str) -> str:
                stem, suf = Path(n).stem, Path(n).suffix
                return (re.sub(r'_\d+$', '', stem) + suf).lower()

            existing = {_base(p['filename']) for p in pending}
            for src in media_keys:
                for item in self.collect_media_from_issue(src):
                    if 'path' not in item:
                        upload_failed.append(
                            f"{item.get('url', '?')[:60]}({item['error']})")
                        continue
                    if _base(item['filename']) in existing:
                        print(f"  [媒体] 跳过重复文件 {item['filename']}")
                        continue
                    existing.add(_base(item['filename']))
                    pending.append(item)

            for item in pending:
                try:
                    self.jira.add_attachment(key, item['path'])
                    uploaded.append(item['filename'])
                    print(f"  [附件] 已上传 {item['filename']} ({item['origin']})")
                except Exception as e:
                    upload_failed.append(f"{item['filename']}({e})")
                    print(f"  [附件] 上传失败 {item['filename']}: {e}")

            if uploaded or upload_failed:
                attachment_result = {
                    'uploaded': uploaded,
                    'failed': upload_failed,
                }

            # 建单后核对兜底：读回关键字段，与提交值不符则自动补写
            verify_result = None
            if verify:
                verify_result = self._verify_and_backfill(key, fields)

            return {
                'success': True,
                'key': key,
                'url': f"{self.jira_url}/browse/{key}",
                'summary': full_summary,
                'assignee': assignee,
                'department': department,
                'bug_level': bug_level,
                'version': version,
                'reproduce_rate': reproduce_rate,
                'attachment': attachment_result,
                'verify': verify_result,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='创建 Jira Bug (智能版) - 支持多项目')
    parser.add_argument('summary', nargs='?', help='问题概要')
    parser.add_argument('-p', '--project', default=None,
                        choices=['NK', 'X1', 'X15'],
                        help='项目 (默认从环境变量读取，可选: NK=K1, X1, X15)')
    parser.add_argument('-f', '--feature', default='', help='功能名称')
    parser.add_argument('-D', '--department', default='auto',
                        choices=['auto', '策划', '客户端', '服务器', '运营', '测试'],
                        help='部门 (默认: auto 自动分析)')
    parser.add_argument('-l', '--level', default='auto', choices=['auto', 'A', 'B', 'C', 'D'], help='Bug等级')
    parser.add_argument('-v', '--version', default='', help='修复版本 (如 0.25.0 或 25)')
    parser.add_argument('--affect-version', default='',
                        help='影响版本（如 线上_qa）；不传则线上bug自动取上一个版本')
    parser.add_argument('-d', '--description', default='', help='详细描述')
    parser.add_argument('-e', '--expected', default='', help='预期结果')
    parser.add_argument('-r', '--actual', default='', help='实际结果')
    parser.add_argument('-a', '--assignee', default='', help='指定经办人')
    parser.add_argument('-t', '--test-key', default='', help='归属功能')
    parser.add_argument('--attachment', default=None, action='append',
                        help='附件路径（可重复传入多个）')
    parser.add_argument('--media-from', default=None, action='append', metavar='CS-KEY',
                        help='从客诉单转存图片/视频作为本单附件（可重复；'
                             '不传则自动从描述里识别 CS 单号）')
    parser.add_argument('--no-auto-media', action='store_true',
                        help='不要自动识别描述里的客诉单号（默认会识别并转存其媒体）')
    parser.add_argument('--online', action='store_true', help='线上 Bug（影响版本会比修复版本低一个）')
    parser.add_argument('--feedback', default='', choices=['', '客服反馈', 'QA反馈', '项目组反馈'],
                        help='反馈来源（线上Bug时添加到标签）')
    parser.add_argument('--reproduce-rate', default='',
                        choices=['', 'Always', 'High', 'Medium', 'Low', 'Once'],
                        help='重现概率（留空则按描述关键词自动识别）')
    parser.add_argument('--no-verify', action='store_true',
                        help='跳过建单后的关键字段核对补写')
    parser.add_argument('-j', '--json', action='store_true', help='JSON输出')

    args = parser.parse_args()

    # 创建时指定项目
    creator = SmartBugCreator(project=args.project)

    if not args.summary:
        parser.error("请提供 Bug 概要")

    result = creator.create_bug(
        summary=args.summary,
        feature=args.feature,
        department=args.department,
        bug_level=args.level,
        version=args.version,
        description=args.description,
        expected=args.expected,
        actual=args.actual,
        assignee=args.assignee,
        related_function=args.test_key,
        attachment=args.attachment or '',
        is_online_bug=args.online,
        feedback_source=args.feedback,
        reproduce_rate=args.reproduce_rate,
        verify=not args.no_verify,
        media_from_issue=args.media_from or '',
        auto_media=not args.no_auto_media,
        affect_version=args.affect_version,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result['success']:
            print(f"\n✓ Bug 创建成功!")
            print(f"  Key: {result['key']}")
            print(f"  概要: {result['summary']}")
            print(f"  部门: {result['department']}")
            print(f"  经办人: {result['assignee']}")
            print(f"  Bug等级: {result['bug_level']}")
            if result.get('version'):
                print(f"  版本: {result['version']}")
            if result.get('reproduce_rate'):
                print(f"  重现概率: {result['reproduce_rate']}")
            att = result.get('attachment') or {}
            if att.get('uploaded'):
                print(f"  附件: {', '.join(att['uploaded'])}")
            if att.get('failed'):
                print(f"  附件失败(需手动处理): {', '.join(att['failed'])}")
            v = result.get('verify') or {}
            if v.get('fixed'):
                print(f"  核对补写: {', '.join(v['fixed'])}")
            if v.get('failed'):
                print(f"  核对补写失败(需手动处理): {', '.join(v['failed'])}")
            if v.get('error'):
                print(f"  核对未完成: {v['error']}")
            print(f"  链接: {result['url']}")
        else:
            print(f"\n✗ 创建失败: {result['error']}")


if __name__ == '__main__':
    main()
