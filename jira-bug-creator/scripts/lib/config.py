# -*- coding: utf-8 -*-
"""配置管理模块 - 支持多项目"""

import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv


# ========== 多项目配置 ==========
# 每个项目的独立配置
# NK = K1_CD(NK)，X1 = X1(X1)
PROJECT_CONFIGS = {
    'NK': {
        'display_name': 'K1_CD(NK)',
        'leaders': {
            '策划': '',
            '客户端': '',
            '服务器': '',
            '运营': '',
            '测试': '',
        },
        'default_related_function': '',
        'gitlab_project': '',
        # NK 项目的 Jira 字段 ID
        'fields': {
            'bug_level': 'customfield_12403',
            'related_function': None,  # NK 没有这个字段
            'reproduce_rate': 'customfield_10028',
            'expected_result': 'customfield_10206',
            'actual_result': 'customfield_10207',
            'reproduce_steps': 'customfield_12000',  # 复现步骤
        },
        # NK 项目的 Bug 等级选项 ID
        'bug_level_ids': {'A': '12006', 'B': '12007', 'C': '12008', 'D': '12009'},
        # NK 项目必填字段
        'required_fields': ['fixVersions', 'versions', 'labels', 'reproduce_steps'],
        # 标签使用功能名
        'use_feature_as_label': True,
        # 功能负责人映射表
        # 格式: '功能名': {'客户端': '用户名', '策划': '用户名', ...}
        'feature_owners': {
            '魔狼试炼': {'客户端': 'hesen', '策划': 'zhangzimian'},
        },
    },
    'X1': {
        'display_name': 'X1(X1)',
        'leaders': {
            '策划': 'fangchao',
            '客户端': 'xionghao',
            '服务器': 'ranbo',
            '运营': 'chenxiaoran',
            '测试': 'lipeijie',
        },
        'default_related_function': '',
        'gitlab_project': '',
        # X1 项目的 Jira 字段 ID (需要确认)
        'fields': {
            'bug_level': 'customfield_12403',
            'related_function': None,
            'reproduce_rate': 'customfield_10028',
            'expected_result': 'customfield_10206',
            'actual_result': 'customfield_10207',
            'reproduce_steps': 'customfield_12000',
        },
        # X1 项目的 Bug 等级选项 ID (需要确认，暂用 NK 的)
        'bug_level_ids': {'A': '12006', 'B': '12007', 'C': '12008', 'D': '12009'},
        'required_fields': ['fixVersions', 'versions', 'labels', 'reproduce_steps'],
        'use_feature_as_label': True,
        # 功能负责人映射表
        'feature_owners': {
            # 示例：
            # '登录': {'客户端': 'zhangsan', '服务器': 'lisi'},
        },
    },
    # X15 项目（早期项目，结构比 NK / X1 更简单：没有 Bug 等级、没有归属功能字段）
    # 通过 scripts/probe-project.py 探测确认 (2026-05-29)
    'X15': {
        'display_name': 'X15(X15)',
        'leaders': {
            '策划': 'fangchao',
            '客户端': 'xionghao',
            '服务器': 'ranbo',
            '运营': '',  # X15 暂无运营 Leader
            '测试': 'lipeijie',
        },
        'default_related_function': '',  # X15 没有归属功能字段
        'gitlab_project': '',
        # X15 项目的 Jira 字段 ID
        # ⚠️ X15 没有"Bug 等级"和"归属功能"字段，显式设为 None 让脚本跳过 payload
        'fields': {
            'bug_level': None,           # X15 createmeta 中无此字段
            'related_function': None,    # X15 createmeta 中无此字段
            'reproduce_rate': 'customfield_10028',
            'expected_result': 'customfield_10206',
            'actual_result': 'customfield_10207',
            'reproduce_steps': 'customfield_12000',
        },
        # 保留 bug_level_ids 但实际不会用（field_bug_level=None 会跳过）
        'bug_level_ids': {'A': '12006', 'B': '12007', 'C': '12008', 'D': '12009'},
        'required_fields': ['fixVersions', 'versions', 'labels', 'reproduce_steps'],
        'use_feature_as_label': True,
        'feature_owners': {},
    },
}


class Config:
    """配置管理类 - 支持多项目"""

    def __init__(self, env_file: Optional[str] = None, project: Optional[str] = None):
        """
        初始化配置

        Args:
            env_file: 环境变量文件路径
            project: 项目 Key (如 X2, K1, X1)，若不指定则从环境变量读取

        查找顺序:
        1. 指定的 env_file
        2. 当前目录 .env
        3. skill 目录 .env
        4. 用户目录 ~/.env.jira
        """
        self._load_env(env_file)
        self._project = project  # 保存指定的项目
        self._validate()

    def _load_env(self, env_file: Optional[str] = None):
        """加载环境变量"""
        # 查找顺序
        search_paths = []

        if env_file:
            search_paths.append(Path(env_file))

        # 当前目录
        search_paths.append(Path.cwd() / '.env')

        # skill 目录
        skill_dir = Path(__file__).parent.parent.parent
        search_paths.append(skill_dir / '.env')

        # 用户目录
        search_paths.append(Path.home() / '.env.jira')

        # 加载第一个存在的文件
        for path in search_paths:
            if path.exists():
                load_dotenv(path)
                self.env_file = str(path)
                return

        self.env_file = None

    def _validate(self):
        """验证必需的配置"""
        self.missing = []

        # Jira 配置
        self.jira_url = os.getenv('JIRA_URL')
        self.jira_token = os.getenv('JIRA_PERSONAL_TOKEN')

        # 项目：优先使用构造函数指定的项目，否则从环境变量读取
        self.jira_project = self._project or os.getenv('JIRA_PROJECT', 'NK')

        if not self.jira_url:
            self.missing.append('JIRA_URL')
        if not self.jira_token:
            self.missing.append('JIRA_PERSONAL_TOKEN')

        # Google Sheets 配置
        self.sheet_spreadsheet_id = os.getenv('SHEET_SPREADSHEET_ID')
        self.sheet_worksheet_id = os.getenv('SHEET_WORKSHEET_ID')

        # 获取项目配置
        project_config = PROJECT_CONFIGS.get(self.jira_project, {})

        # 部门 Leader - 优先从项目配置读取，fallback 到环境变量
        project_leaders = project_config.get('leaders', {})
        self.leaders = {
            '策划': project_leaders.get('策划') or os.getenv(f'LEADER_PLANNER_{self.jira_project}') or '',
            '客户端': project_leaders.get('客户端') or os.getenv(f'LEADER_CLIENT_{self.jira_project}') or '',
            '服务器': project_leaders.get('服务器') or os.getenv(f'LEADER_SERVER_{self.jira_project}') or '',
            '运营': project_leaders.get('运营') or os.getenv(f'LEADER_OPERATION_{self.jira_project}') or '',
            '测试': project_leaders.get('测试') or os.getenv(f'DEFAULT_TEST_ASSIGNEE_{self.jira_project}') or '',
        }

        # 默认值 - 优先从项目配置读取
        self.default_test_assignee = self.leaders.get('测试', '')
        self.default_reproduce_rate = os.getenv('DEFAULT_REPRODUCE_RATE', 'Always')
        self.default_related_function = (
            project_config.get('default_related_function') or
            os.getenv(f'DEFAULT_RELATED_FUNCTION_{self.jira_project}') or
            os.getenv('DEFAULT_RELATED_FUNCTION', '')
        )

        # GitLab 项目路径
        self.gitlab_project = (
            project_config.get('gitlab_project') or
            os.getenv(f'GITLAB_PROJECT_{self.jira_project}') or
            os.getenv('GITLAB_PROJECT', '')
        )

        # Jira 自定义字段 ID (通常同一 Jira 实例是共享的)
        self.field_related_function = os.getenv('JIRA_FIELD_RELATED_FUNCTION', 'customfield_12901')
        self.field_bug_level = os.getenv('JIRA_FIELD_BUG_LEVEL', 'customfield_10205')
        self.field_reproduce_rate = os.getenv('JIRA_FIELD_REPRODUCE_RATE', 'customfield_10028')
        self.field_expected_result = os.getenv('JIRA_FIELD_EXPECTED_RESULT', 'customfield_10206')
        self.field_actual_result = os.getenv('JIRA_FIELD_ACTUAL_RESULT', 'customfield_10207')

        # Issue 类型 ID
        self.issuetype_bug = os.getenv('JIRA_ISSUETYPE_BUG', '10004')
        self.issuetype_task = os.getenv('JIRA_ISSUETYPE_TASK', '10002')

    @staticmethod
    def get_available_projects() -> list:
        """获取所有可用的项目列表"""
        return list(PROJECT_CONFIGS.keys())

    def get_user_email(self, username: str) -> Optional[str]:
        """获取用户邮箱映射"""
        return os.getenv(f'USER_{username}')

    def get_leader(self, department: str) -> str:
        """获取部门 Leader"""
        return self.leaders.get(department, self.leaders.get('UI'))

    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return len(self.missing) == 0

    def get_setup_guide(self) -> str:
        """获取配置指南"""
        guide = []
        guide.append("=" * 50)
        guide.append("Jira Bug Creator 配置指南")
        guide.append("=" * 50)

        if self.missing:
            guide.append(f"\n缺少以下必需配置: {', '.join(self.missing)}")

        guide.append("\n1. 复制配置模板:")
        guide.append("   cp .env.example .env")
        guide.append("\n2. 编辑 .env 文件，填入以下内容:")
        guide.append("   JIRA_URL=https://jira.tap4fun.com/")
        guide.append("   JIRA_PERSONAL_TOKEN=your_token_here")
        guide.append("\n3. 获取 Jira Token:")
        guide.append("   Jira 个人设置 → Personal Access Tokens → 创建新 Token")
        guide.append("\n4. 配置 Pipedream MCP (用于读取 Google Sheets):")
        guide.append("   Cursor 设置 → MCP → 添加 https://mcp.pipedream.net/v2")
        guide.append("\n详细说明: references/setup-guide.md")
        guide.append("=" * 50)

        return '\n'.join(guide)
