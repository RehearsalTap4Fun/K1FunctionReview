# K1FunctionReview

K1 功能审核 skill：需求对齐、静态预检、运行验收，以及线上游戏服/战场服备份与个人测试环境准备。

完整入口：[review-k1-function/SKILL.md](review-k1-function/SKILL.md)。

用户明确要求提交 Jira Bug 时，使用 [jira-bug-creator/SKILL.md](jira-bug-creator/SKILL.md)。此技能提供 NK 建单脚本和空配置模板，不包含个人凭证。

流程讲解：[完整 SVG 动作流](docs/workflow/k1-skill-workflow.svg) · [分步演示 HTML](docs/workflow/k1-skill-workflow-demo.html)。演示包含测试用例生成、反馈表查找与新建、缺字段补建、逐项反馈维护及验收收尾；下载 HTML 与同目录 SVG 后用浏览器打开，支持步骤切换与缩放。

## 内容

- `review-k1-function/scripts/`：完整工作流、Jenkins/钉钉结果关联、运行探针、验收与证据处理脚本。
- `review-k1-function/references/`：流程合同、外部依赖、凭证配置和使用说明。
- `slg-testcase-generator/`：随仓库分发的团队用例生成 Skill；K1 静态预审遵循完整覆盖规则，在线写表依赖仅供独立标准流程使用。
- `jira-bug-creator/`：随仓库分发的 K1/NK Jira 建单 Skill；用户明确要求提 Bug 时整理证据、提交并回读。
- `review-k1-function/features/`：[按功能整理的验收经验与可复用脚本](review-k1-function/features/index.md)；验收前读取对应档案，阶段结束或中断前更新。历史结论与本轮验证分开记录。
- `review-k1-function/assets/`：空配置/请求模板、Unity 执行配方、场景/重放定义及本地验收工作台资源；不是运行记录。
- `tests/`：使用本地协议 fixture 的 Jenkins 与环境整链回归，不连接实际 Jenkins/钉钉/SSH。

## 安装与依赖

先读[外部依赖与首次配置](review-k1-function/references/dependencies-and-setup.md)。

K1 工程根目录由用户在每轮任务中提供，不能从系统默认目录、环境变量或历史报告自行选定。三端仓库的相对布局见 [K1 项目合同](review-k1-function/references/k1-project.md)；macOS 步骤见 [安装与首次配置](review-k1-function/references/macos-setup.md)。FunctionPreview 可安装在自选位置；在选定的父目录执行：

```powershell
git clone https://github.com/RehearsalTap4Fun/K1FunctionReview.git
```

然后把项目内的 `review-k1-function`、`slg-testcase-generator` 和 `jira-bug-creator` 三个完整目录分别注册或链接到你使用的 Agent skills 目录。不能只复制 `SKILL.md`；使用其他目录或平台前需适配并验证脚本中的路径约束。已有同名项目目录时，不要覆盖现有工作。

自动建环境需要 Python 3.10+、PowerShell、Git、DWS、Node.js、mcporter，以及本人 Jenkins/Git/钉钉/K1 MCP 访问权限。`slg-testcase-generator`、`jira-bug-creator` 已随仓库提供；其他 skill 按具体审核场景准备，详见依赖表。备份部署脚本使用标准库；Excel 功能按需安装 `requirements-optional.txt`。

## 配置与使用

把[空 Jenkins 配置模板](review-k1-function/assets/jenkins-local-config.example.json)复制到自己的私有位置，填写本人 `username`、`apiToken`、`baseUrl` 和 `environmentWorkflow`。发布版没有预设内部通知群、机器人身份或测试节点，空值会阻止执行。配置可放在用户提供的 K1 工程根目录下 `K1Game/.jenkins.local.json`，也可用 `--config` 指定。

随后按[测试环境流程](review-k1-function/references/jenkins-test-environment.md)填写线上 SID、代码分支、配表分支与实际授权，执行 `prepare` 和可续跑的 `advance`。战场服使用 `battle`；未指定 KVK 保留列表全量恢复，指定则按列表保留。环境 `ready` 不代表功能验收通过。

Unity 适配器同样是未绑定的模板，须核验实际源码与当前账号/会话再使用。除本仓库内的 `slg-testcase-generator`、`jira-bug-creator` 外，其他外部 skill 和 CLI/MCP 服务不随仓库打包。

## 本地验证

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

本仓库不包含个人凭证、登录态、运行回执、报告或缓存。`.gitignore` 已排除常见本地配置与运行目录；实际配置及已绑定的 Unity 适配器应保存在仓库外或被忽略的私有目录中。
