# 分享、外部依赖与首次配置

本说明用于分享给同事、迁移机器或首次执行。只检查本次任务需要的能力；已配置且已核验的依赖无需反复询问。安装 skill 只提供流程说明和脚本，不会自动授予 Jenkins、钉钉、Git 或测试服务器访问权限。

## 按场景准备

| 使用场景 | 外部 skill | 工具与访问要求 |
|---|---|---|
| 线上服备份 → DownKey → 个人测试服部署 → 运行校验 | 建议同时提供 `dws`，便于认证和故障排查；正常整链由本 skill 脚本执行，无须其他 skill 才能运行 | Python、PowerShell、Git；已登录的 DWS CLI；Node.js + mcporter；名为 `k1-mcp` 的 MCP 服务及 `ssh_exec`；个人 Jenkins API Token；代码/配表 Git 读取权限；公司内网/VPN |
| 正式 K1 配置检查 | `config-table-editor`，检查正式 `.xlsx` 时需要 | 配置仓库读取权限；需要时 Git LFS；Excel 解析环境，例如 `openpyxl`。只读导出副本，不修改正式配置 |
| 缺少用例、需要从需求生成用例 | `slg-testcase-generator` | 可访问需求文档及必要项目知识；本地 Markdown 交付不要求 Google Drive/API Key |
| Unity 客户端实测/GM/故障模拟 | 建议 `unity-mcp-orchestrator`（目录也可能名为 `unity-mcp-skill`） | 对应版本 Unity Editor、打开的 K1 客户端项目、MCP for Unity 连接和实际可用的项目工具、授权测试账号 |
| 钉钉需求文档、反馈表 | 走 CLI 时使用 `dws`；已连接的文档工具也可按原路由使用 | 本人的钉钉登录态和目标文档/表格权限；维护时需要编辑权限；图片追加等浏览器步骤还需可用的浏览器工具及登录态 |
| Word / PDF 需求材料 | 分别按文档路由使用 `documents:documents` / `pdf:pdf` | 对应 skill 自身运行依赖；本地文件不需要统一的额外 API Key |
| Jira 单号定位 / Confluence 文档 | 按实际来源选择已配置连接；用 Confluence 时可配 `confluence` | 本人的 Jira/Confluence 访问凭证或有效登录态。直接提供分支与可读本地需求时，不强制配置这两项 |

`jenkins-hotfix` 不是测试环境链的依赖；不得用正式热更任务代替个人测试服部署。K1 配置检查不使用 `xcfg-tool`。这些外部 skill 不包含在当前 skill 文件夹内，分享时应列出名称并让接收者从团队维护来源安装；不要假设对方已有本机全部 skill。

## 自动建环境所需凭证

| 项目 | 接收者需要准备什么 | 保存位置与说明 |
|---|---|---|
| Jenkins | 自己的 `username` 和 `apiToken`，以及服务 `baseUrl` | 默认读取 `C:/Project/K1Game/.jenkins.local.json`；也可每次通过 `--config <本地文件>` 指定。用户名同时决定个人测试容器归属，不能照抄分享者账号 |
| Git | 服务端、配表仓库的读取凭证；完整审核还需客户端仓库 | 使用个人 SSH key/agent 或 Git credential helper，包含必要的 LFS 读取权限。远端快照是非交互式执行，凭证必须预先可用 |
| DWS | 本人钉钉 OAuth 登录及读取备份通知群历史消息的权限 | DWS 管理登录态，按 `dws auth --help` / `dws auth login --help` 配置。正常使用无需把 access token 填进本 skill；组织使用自建 OAuth 应用时，另由管理员提供对应 AppKey/AppSecret 配置 |
| K1 MCP | 被授权访问团队 `k1-mcp` 服务的个人连接配置；服务端能执行目标测试节点的只读 SSH 探针 | 配置在接收者自己的 MCP/mcporter 中。若网关要求 API Key/Token，在该连接的本地配置中填写；本脚本没有独立的 K1 API Key 字段，不猜测网关字段名 |

当前脚本调用的是 **`mcporter call k1-mcp.ssh_exec`**。仅在 Codex 工具列表看到同名 MCP 不保证 mcporter 能发现它，须核验接收者本地 mcporter 配置；服务名称也必须匹配。SSH 认证由既有 MCP 服务管理，通常不需要再把服务器私钥交给 skill。

Jenkins 至少需可读取“指定备份线上服”“自定义代码配表分支启动个人远程服”及实际下游“个人远程服务器部署”的参数、队列、构建记录和日志，并具备前两项的构建权限。测试节点的 MCP 账号需能执行 `hostname`、`docker ps -a`、`docker inspect`、`docker top`、`docker logs` 和 Python 只读探针。依赖清单不替代对具体线上 SID 备份、测试数据导入与本人实例重建的用户授权。

本 skill 的脚本不直接调用 OpenAI API，因此不额外要求 OpenAI API Key。运行它的宿主本身如何登录/计费，由接收者自己的环境决定。**DownKey 是每次备份产生的临时结果，不是安装时应共享或预填的 API Key**；本地不需要另装 `file-ladder` 来取得它。

## 本地配置模板

分享包提供无凭证模板 [assets/jenkins-local-config.example.json](../assets/jenkins-local-config.example.json)。接收者复制到自己的默认配置位置或其他私有位置，再在本地填写 `baseUrl`、`username`、`apiToken`；模板中的空值不能直接执行。不要把填写后的文件加入 Git 或分享包。

发布版的 `environmentWorkflow` 必须填写 `groupId`、`sender`、`senderId`、`runtimeHost`。本仓库不预填内部群、机器人身份或测试节点；由接收者先只读确认，再写入自己的本地配置。这些是环境标识，不是访问密钥，填写标识不会自动获得权限。

## 运行环境与目录

- 当前使用路径为 Windows：本地 Python **3.10 或以上**、可调用的 `powershell`、Git。需要读取 LFS 工作簿时还需 Git LFS。备份部署脚本使用 Python 标准库；正式 Excel 解析与 `acceptance/config_variants.py` 需要 `openpyxl`。`pytest`、skill 校验使用的 `PyYAML` 只在开发/验证 skill 时需要。
- 自动建环境另需 DWS CLI、Node.js、mcporter；命令应可被当前进程发现。当前 Windows 适配器会寻找 mcporter 安装目录下的 `node_modules/mcporter/dist/cli.js`，可先核验入口存在；不兼容的安装布局须适配后再运行。
- 远程测试节点需可用的 `python3`（当前探针使用 Python 3.6+ 标准库）、Docker CLI 和前述读取权限。仅本地安装 Docker 不能替代远程节点权限。
- 源码目录约定为 `C:/Project/K1Client/k1_client`、`C:/Project/K1Game/game`、`C:/Project/K1Dataconfig/dataconfig`，各自存在可用的 `origin`。仅部署环境需要 server/config 两端；完整审核按三端准备。
- 默认项目位置为 `C:/Project/FunctionPreview`，skill 位于其中的 `review-k1-function/`。脚本包含固定 K1 仓库路径、由脚本位置推导的项目根目录和写入边界，**不是复制到任意 skills 目录就能直接运行的通用包**。接收者可按此布局放置项目，再把 skill 注册/链接到自己的 skills 目录；不同目录或平台需同时适配脚本、合同和验证，不能只改说明中的路径。
- 分享完整 `review-k1-function/` 实体内容，包括 `SKILL.md`、`agents/`、`scripts/`、`references/`、`assets/`。本机安装入口是 Junction，不能只发这个链接，也不能只发 `SKILL.md`。若分享整个 FunctionPreview 项目，不包括 `.tmp`、`.cache`、`reports` 和用户配置；运行记录可能含内部数据与访问定位。

## 首次使用的提示与只读检查

先按本次任务给接收者一份简短清单：**必需依赖、已检测项、缺失项、凭证应在哪本地配置**。凭证只核对必填字段是否存在且非空；不显示值，不读取/输出完整 MCP 连接配置或含 token 的 URL，也不要求用户在聊天中粘贴密钥。

1. 核验完整目录和必要的外部 skill；按所选阶段检查 `python`、`powershell`、`git`、`dws`、`node`、`mcporter` 可执行文件及需要的库。
2. 核验个人 Jenkins 配置存在、DWS 已登录、Git 凭证已就绪、mcporter 能找到 `k1-mcp.ssh_exec`。只报告连接名、登录/可用状态与缺口。
3. 使用 `jenkins_test_environment.py inspect --config <本地配置>` 只读检查 Jenkins；按需要通过现有适配器只读验证消息来源与测试节点。群消息可能包含 DownKey，不把原始 DWS 输出写进聊天或报告。
4. 只读检查成功不等于具备 Jenkins 构建权限。缺权限/连接时明确说明对应阶段不可执行，并继续不依赖它的部分；不要为“试权限”触发构建，也不要因缺少 Unity、Word 等无关依赖阻塞单独部署任务。

依赖齐备且操作范围已有授权后，按 [jenkins-test-environment.md](jenkins-test-environment.md) 执行原流程，无需重复批准同一范围。

## 发布版 Unity 模板

`assets/acceptance/unity/gold-miner-adapter.json` 不包含真实账号、活动、会话、程序集绑定或过去的验证结果。使用前核验实际源码 SHA/文件哈希并读取当前 Unity 身份，将模板另存到本机的私有运行目录；保留空值时不可直接执行。
