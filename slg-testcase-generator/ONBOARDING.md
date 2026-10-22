# K1 团队接入说明
此目录已随 K1FunctionReview 仓库分发。使用 `review-k1-function` 做静态预审时，直接从仓库内注册此 Skill，并遵循 [K1 静态用例规则](references/static_acceptance.md)：完整覆盖、无累计时间或条数上限；不需要 Google 认证或在线写表依赖。以下工作区配置、Python requirements 和 Google 认证只用于独立的标准在线用例流程。

此共享包保留通用用例规则、K1 项目配置、知识库、需求/用例参考、有效脚本和测试。个人登录令牌、实际脚本配置、历史输出及缓存不随包分发。

## 1. 安装 Skill

解压后保持顶层目录名为 `slg-testcase-generator`，将整个目录复制到所用客户端的 Skill 目录：

- Codex：`$CODEX_HOME/skills/slg-testcase-generator`；未设置 `CODEX_HOME` 时使用用户目录下的 `.codex/skills/slg-testcase-generator`。
- Cursor：用户目录下的 `.cursor/skills/slg-testcase-generator`。

更新已有安装前，先保留自己的配置和凭证，并比较团队配置是否有本地修改。以下命令中的 `<Skill目录>` 和 `<K1工作区>` 均需替换为本机实际路径。

## 2. 配置 K1 工作区

标准流程从当前工作区读取 `testcase-config/project_config.md`。首次接入时，将包内 `K1-testcase-config/` 复制到 K1 工作区并命名为 `testcase-config/`：

```powershell
Copy-Item -LiteralPath '<Skill目录>/K1-testcase-config' -Destination '<K1工作区>/testcase-config' -Recurse
New-Item -ItemType Directory -Path '<K1工作区>/testcase-config/output' -Force
```

仅对尚未配置 `testcase-config/` 的工作区执行复制；已有配置的工作区按需合并更新。

| 文件/目录 | 用途 |
|---|---|
| [K1-testcase-config/project_config.md](K1-testcase-config/project_config.md) | 团队 Drive 路径、模板、跟踪表、知识库入口 |
| `K1-testcase-config/game_knowledge/` | K1 玩法和通用系统补充 |
| `K1-testcase-config/doc/` | 需求、人工用例和写法分析，按功能选读 |
| [K1-testcase-config/config.json.example](K1-testcase-config/config.json.example) | 工作区脚本配置示例 |

保留的 Drive/Sheets ID 是团队资源标识。使用在线流程的协作者需要自己的 Google 账号具备相应资源访问权限。

## 3. 安装 Python 依赖

在 Skill 根目录执行以下 PowerShell 命令：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item -LiteralPath 'scripts/config.template.json' -Destination 'scripts/config.json'
```

编辑本机 `scripts/config.json`：

- `google_sheet_id`：用于认证后的读取验证，填写自己有权限访问的表格 ID。
- `template_sheet_id`、`testcase_root_folder_id`：按 K1 项目配置填写。
- `google_sheets_credentials_file`：需要使用该字段的工具按本机凭证路径填写；下述 OAuth 认证脚本固定查找 `scripts/credentials.json`，其次查找 Skill 根目录的同名文件。
- `gemini_api_key`：仅可选的 Gemini 解析功能需要；不使用时设为空字符串。

`auth_setup.py`、`excel_tool.py` 的命令行入口读取 `scripts/config.json`。如使用会从工作区读取配置的 `sheets_writer.py`，还需将工作区 `testcase-config/config.json.example` 复制为 `config.json` 并填写实际值。

## 4. 完成自己的 Google 认证

将团队提供或自行创建的桌面 OAuth 客户端凭证放到 `scripts/credentials.json`，然后在 Skill 根目录执行：

```powershell
.\.venv\Scripts\python.exe scripts/auth_setup.py
```

脚本会打开浏览器完成授权，将登录令牌保存为 `scripts/token.json`，并尝试只读访问配置的 `google_sheet_id`。令牌不随共享包提供，每位协作者用自己的账号授权。

K1 静态预审模式只输出本地 Markdown，用法见 [references/static_acceptance.md](references/static_acceptance.md)，无需上述在线写表配置。

## 5. 开始使用

在配置好 `testcase-config/` 的 K1 工作区中，向 AI 提供 PRD 和 UX 材料，并请求生成测试用例。完整规则见 [SKILL.md](SKILL.md)。

| 脚本 | 用途 |
|---|---|
| `scripts/excel_tool.py` | 读取需求和配置表 |
| `scripts/validate_cases.py` | 本地检查用例 JSON |
| `scripts/write_test_cases.py` | 标准流程向指定用例 Sheet 写入数据 |
| `scripts/write_cases_to_sheet.py` | K1 项目辅助流程：创建用例表、填写评审信息并更新跟踪表 |

`write_cases_to_sheet.py` 从 **Skill 包内**的 `K1-testcase-config/project_config.md` 读取用例根目录，按名称查找周期文件夹或根目录中的模板，跟踪表则由脚本内的 `TRACKER_SPREADSHEET_ID` 指定。标准流程读取 **工作区**的 `testcase-config/project_config.md`。若调整团队资源，应核对各自实际读取的位置；仅修改工作区配置不会改变该辅助脚本的全部目标。脚本行为保持不变。

输出文件保存到工作区的 `testcase-config/output/`；如需使用包内 `K1-testcase-config/output/`，请在首次输出时自行创建。共享包不附带历史输出。

## 6. 再次分享与维护

`.gitignore` 已排除实际 `config.json`、登录令牌、OAuth 凭证、缓存和用例输出。**直接压缩文件夹不会应用 Git 忽略规则**，再次打包时仍需排除这些本机文件以及 `.venv/`。

保留 `tests/` 便于后续修改时检查K1 静态预审模式和兼容契约。需要运行现有测试时，在自己的环境另行安装 `pytest`，然后从 Skill 根目录执行 `python -m pytest tests`。
