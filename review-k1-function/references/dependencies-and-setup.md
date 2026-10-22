# 分享、外部依赖与首次配置

本说明用于分享给同事、迁移机器或首次执行。只检查本次任务需要的能力；已配置且已核验的依赖无需反复询问。安装 skill 只提供流程说明和脚本，不会自动授予 Jenkins、钉钉、Git 或测试服务器访问权限。

分享时包含 [功能经验索引](../features/index.md)、对应档案、[读写规则](feature-experience.md)、档案模板及 `features/<featureId>/scripts/` 中被引用的运行模板和说明。档案中的本地证据路径仅作溯源，原始运行回执、账号快照和凭证不随包分发；接收者标记无法访问的来源，并在当前版本复核后使用。确认 Skill 目录可写以便持续沉淀；不可写时按读写规则保存本轮待回写增量。

从零配置自动建环境时，先按仓库 README 准备 FunctionPreview、Python/Git 及 server/config 仓库，再依次完成本文的 MCP/mcporter、DWS 登录、Jenkins Token 和环境标识配置，最后执行只读检查。凭证文件和登录态均由使用者在自己电脑上建立。

## 按场景准备

| 使用场景 | 外部 skill | 工具与访问要求 |
|---|---|---|
| 线上服备份 → DownKey → 个人测试服部署 → 运行校验 | 建议同时提供 `dws`，便于认证和故障排查；正常整链由本 skill 脚本执行，无须其他 skill 才能运行 | Python、PowerShell、Git；已登录的 DWS CLI；Node.js + mcporter；名为 `k1-mcp` 的 MCP 服务及 `ssh_exec`；个人 Jenkins API Token；代码/配表 Git 读取权限；公司内网/VPN |
| 正式 K1 配置检查 | `config-table-editor`，检查正式 `.xlsx` 时需要 | 配置仓库读取权限；需要时 Git LFS；Excel 解析环境，例如 `openpyxl`。只读导出副本，不修改正式配置 |
| 缺少用例、需要从需求生成用例 | 仓库内 `slg-testcase-generator/`，需将完整目录注册到 Agent skills | 可访问已确认并回读的需求文档；K1 静态 Markdown 用例无累计时间或数量上限，不要求 Google Drive/API Key。独立在线写表流程才需该 Skill 的额外依赖 |
| Unity 客户端实测/GM/故障模拟 | 建议 `unity-mcp-orchestrator`（目录也可能名为 `unity-mcp-skill`） | 对应版本 Unity Editor、打开的 K1 客户端项目、MCP for Unity 连接和实际可用的项目工具、授权测试账号 |
| 钉钉需求文档、反馈表 | 走 CLI 时使用 `dws`；已连接的文档工具也可按原路由使用 | 本人的钉钉登录态和目标文档/表格权限；维护时需要编辑权限；图片追加等浏览器步骤还需可用的浏览器工具及登录态 |
| 版本进包项进度播报 | 本 skill 的 Python 脚本 | 用户指定并授权的自定义机器人 Webhook；按 [播报配置](acceptance-progress.md#机器人私有配置) 存本地私有文件，不随 Skill 分享 |
| Word / PDF 需求材料 | 分别按文档路由使用 `documents:documents` / `pdf:pdf` | 对应 skill 自身运行依赖；本地文件不需要统一的额外 API Key |
| Jira 单号定位 / Confluence 文档 | 按实际来源选择已配置连接；用 Confluence 时可配 `confluence` | 本人的 Jira/Confluence 访问凭证或有效登录态。直接提供分支与可读本地需求时，不强制配置这两项 |

`jenkins-hotfix` 不是测试环境链的依赖；不得用正式热更任务代替个人测试服部署。K1 配置检查不使用 `xcfg-tool`。`slg-testcase-generator` 与本 skill 一同包含在 K1FunctionReview 仓库中，但仍需分别注册到 Agent skills 目录。其余外部 skill 不包含在当前 skill 文件夹内，分享时应列出名称并让接收者从团队维护来源安装；不要假设对方已有本机全部 skill。

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

## 安装 k1-mcp 与 mcporter（Windows）

### 1. 确认内网连接

`k1-mcp` 是团队已部署的远程 MCP 服务，使用者添加连接即可，无需在个人电脑安装服务端。当前团队地址为 `http://172.20.90.39:8443`，协议为 HTTP；按此完整地址配置，不自行追加 `/mcp` 或 `/sse`。需要能访问公司内网或对应 VPN，可在 PowerShell 只读检查端口：

```powershell
Test-NetConnection 172.20.90.39 -Port 8443
```

`TcpTestSucceeded: True` 只表示端口可达，后面仍需验证 MCP 工具发现。本机参考连接没有额外 API Key 或认证头；接收者若遇到认证要求，应向服务维护者获取自己的配置，不能复制他人凭证。此服务地址与 Jenkins 配置中的 `runtimeHost` 含义不同，不从 MCP 地址自动推定部署节点。

### 2. 在使用的 Agent 中添加连接

Codex 与 Cursor 按实际使用情况选配，不要求同时安装两者。已有同名连接时先核对，保留已有认证设置，避免重复添加。

**Codex：** 已有 Codex CLI 时执行：

```powershell
codex mcp add k1-mcp --url http://172.20.90.39:8443
```

也可把下面内容合并到当前用户的 `~/.codex/config.toml`，两种方式选一种：

```toml
[mcp_servers.k1-mcp]
url = "http://172.20.90.39:8443"
```

保存后重新打开会话，确认工具列表可发现 `k1-mcp`。配置格式见 [OpenAI 官方 MCP 接入说明](https://developers.openai.com/learn/docs-mcp)。

**Cursor：** 在当前用户的 `~/.cursor/mcp.json` 中合并以下条目，保留原有的其他服务，然后重启 Cursor：

```json
{
  "mcpServers": {
    "k1-mcp": {
      "type": "http",
      "url": "http://172.20.90.39:8443"
    }
  }
}
```

Windows 下 `~` 表示当前用户目录。上述文件属于个人客户端配置，不放进 skill 分享目录。

### 3. 安装 Node.js 和 mcporter

自动建环境脚本还需要独立的 mcporter CLI。先从 [Node.js 官方下载页](https://nodejs.org/en/download)安装当前受支持的 LTS 版本，选择适合自己电脑的 Windows 安装包，保留 npm 并加入 PATH；安装后重新打开 PowerShell。

下面固定使用本 skill 已核验的 `mcporter 0.9.0`。该包声明 Node.js 最低版本为 `20.11.0`，这是兼容下限，不是建议安装已停止支持的 Node.js 版本。已有可用安装时先检查版本，无需重复安装或降级。

```powershell
node --version
npm.cmd --version
npm.cmd install -g mcporter@0.9.0
mcporter.cmd --version
```

Windows 示例使用 `npm.cmd` / `mcporter.cmd`，避免 PowerShell 对同名 `.ps1` 包装器的执行策略限制，无需为此修改系统执行策略。mcporter 项目说明见 [官方仓库](https://github.com/openclaw/mcporter)。

### 4. 给 mcporter 添加同名连接

首次配置时执行：

```powershell
mcporter.cmd config add k1-mcp --url http://172.20.90.39:8443 --scope home
```

`--scope home` 将连接保存到当前用户配置，使从 FunctionPreview 项目运行的脚本也能发现它。仅在 Codex/Cursor 添加连接不能替代这里的核验；服务名必须为 `k1-mcp`，因为脚本按 `k1-mcp.ssh_exec` 调用。已有同名配置时先核对其来源和地址，不覆盖自定义认证。不要把完整连接配置或认证信息提交到 GitHub。

### 5. 只读验证与常见问题

在 FunctionPreview 项目目录中执行：

```powershell
Set-Location C:/Project/FunctionPreview
mcporter.cmd list k1-mcp
$mcporterEntry = Join-Path (Split-Path (Get-Command mcporter.cmd -ErrorAction Stop).Source) 'node_modules/mcporter/dist/cli.js'
Test-Path -LiteralPath $mcporterEntry
```

通过标准：mcporter 能读取该服务的工具列表，包含 `ssh_exec`，且最后的安装入口检查返回 `True`。这些命令只做工具发现和本地路径检查，不触发 Jenkins 构建或执行服务器业务操作；它们也不证明具体 SSH/Docker 权限已满足，实际节点探针按后续只读预检执行。

- 找不到 `node`、`npm.cmd` 或 `mcporter.cmd`：重新打开终端，检查 Node.js 安装和 npm 全局安装目录是否在 PATH。可用 `npm.cmd prefix -g` 查看全局目录。
- 连接超时或端口不可达：检查内网/VPN、服务地址和服务状态；不要通过触发构建来测试连接。
- Agent 中可用但 mcporter 报服务不存在：在实际执行脚本的同一用户和项目目录下核对 mcporter 配置；项目配置或环境覆盖可能指向其他连接。
- 缺少 `ssh_exec`、出现认证/权限错误，或安装入口返回 `False`：分别核对服务工具授权、本人认证配置、npm 全局安装布局。脚本报 `MCPORTER_NODE_ENTRY_UNAVAILABLE` 时需修复 Node.js/入口路径；不要借用他人密钥或绕过权限。

## 安装 DWS 与个人登录（Windows）

### 1. 安装 CLI 和对应 skill

在尚未安装 DWS 的电脑上，新开 PowerShell，按 [DWS 官方安装说明](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/blob/main/README_zh.md)执行。以下固定为本工作流已核验的 [v1.0.35](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/releases/tag/v1.0.35)，并选择与依赖表名称一致的单入口 `dws` skill（`mono`）：

```powershell
$env:DWS_VERSION = 'v1.0.35'
$env:DWS_SKILL_MODE = 'mono'
Invoke-RestMethod 'https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.ps1' | Invoke-Expression
```

这是官方远程安装脚本，会安装 CLI 和 skill；安装器的环境变量见 [官方 Windows 安装脚本](https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.ps1)。已有 DWS 或自定义 skill 时先核对版本和安装目标，不直接重装、降级或覆盖。已有新版拆分 skill（如 `dingtalk-chat`）时可沿用，CLI 能力与权限需按下面步骤核验，不为改名称重复安装。

安装完成后重新打开 PowerShell 和 Agent，以刷新 PATH 和 skill 发现：

```powershell
Get-Command dws -ErrorAction Stop
dws version --format json
dws auth login --help --format json
```

默认二进制位置为当前用户的 `~/.local/bin/dws.exe`。找不到命令时检查该目录是否加入当前用户 PATH。CLI 安装完成后还要确认宿主能发现 `dws` 或相应产品 skill；CLI 与 skill 是两项依赖，安装 skill 本身不建立钉钉登录态。

### 2. 使用本人钉钉账号授权

普通本机环境执行：

```powershell
dws auth login --format json
```

根据 CLI 打开的浏览器或显示的授权入口，使用本人钉钉账号扫码/授权，选择拥有 K1 通知群访问权限的企业。当前核验版本默认通过本机 `127.0.0.1` 回调完成登录。SSH、容器或无本地浏览器的环境改用设备流，按提示在可用浏览器完成授权：

```powershell
dws auth login --device --format json
```

两种方式选一种。授权后在本机检查：

```powershell
dws auth status --format json
```

查看是否已认证、企业/账号是否正确；CLI 管理本人的登录态及续期，不需要把 access token、refresh token 填入本项目。状态检查在不同版本可能刷新凭证，不把它描述为完全不写本地状态的操作。若需要重新授权，先按当前 `dws auth login --help --format json` 核对后执行 `dws auth login --force --format json`。

普通用户先走默认 OAuth。企业未开通 CLI 时，按授权页提示向管理员申请 CLI 访问，开通后重新登录；自建 OAuth 应用场景由企业管理员提供 AppKey/AppSecret 及回调配置。这些应用配置不能替代个人授权。不要在共享命令、文档或聊天中填写真实密钥，不导出或共享登录态，也不运行 `auth reset` 作为常规安装步骤。

### 3. 验证通知群权限并取得环境标识

先搜索维护者告知的备份通知群：

```powershell
$notificationGroupName = Read-Host '输入备份通知群名称'
dws chat search --query $notificationGroupName --limit 20 --format json
```

按真实返回和维护者确认目标群；同名群不能随便选。后续 `--group` 要求的是 `openConversationId`，不是群名称或内部 numeric groupId。若搜索结果中字段名称不同，以实际消息的 `openConversationId` 和当前 CLI 帮助核验，不编造标识。

选择一段已知有备份机器人通知的时间，只在内存读取消息，输出群与机器人标识，不输出消息正文：

```powershell
$notificationGroup = Read-Host '输入已确认的 openConversationId'
$notificationSince = Read-Host '输入历史通知起始时间（yyyy-MM-dd HH:mm:ss，北京时间）'
$notificationRaw = dws chat message list --group $notificationGroup --time $notificationSince --limit 20 --format json
if ($LASTEXITCODE -ne 0) { throw 'DWS 消息读取失败；在本机核对权限与命令帮助，不输出原始消息。' }
try { $notificationResult = $notificationRaw | ConvertFrom-Json -ErrorAction Stop }
catch { throw 'DWS 返回内容不是有效 JSON；仅在本机排查，不复制原始消息。' }
if ($notificationResult.success -ne $true -or $null -eq $notificationResult.result.messages) {
    throw 'DWS 未返回预期消息结构；核对 CLI 版本、企业能力和群权限。'
}
$notificationResult.result.messages |
    Where-Object { $_.sendType -eq 'robot' } |
    Select-Object openConversationId, sender, senderOpenDingTalkId, createTime
$notificationRaw = $null
$notificationResult = $null
```

把确认属于备份通知机器人的 `sender` 和 `senderOpenDingTalkId` 分别填入 Jenkins 本地配置的 `environmentWorkflow.sender`、`senderId`；消息的 `openConversationId` 填入 `groupId`。仅靠显示名无法区分机器人，须核对稳定 ID；不把其他通知机器人的记录混用。

能登录不代表能读取该群历史。空结果只说明本次窗口没有可见消息；检查时间、分页、群成员及历史消息权限，必要时联系维护者确认，不能为补齐安装配置触发新备份。若命令不存在或只打印父级帮助，使用 `dws chat --help --format json` 和 `dws chat message list --help --format json` 核对当前企业能力；当前工作流要求 `result.messages`、`result.hasMore` 及消息身份字段，不把不同版本的返回结构直接当作可用。

## 获取 Jenkins API Token 并配置

### 1. 准备账号和任务权限

向团队维护者取得 Jenkins 基础地址和本人账号。先确认可在浏览器登录，并能访问“指定备份线上服”“自定义代码配表分支启动个人远程服”和实际下游“个人远程服务器部署”。脚本需要这些任务及相关队列、构建记录、参数和日志的读取权限，以及前两项的构建权限；授权范围由管理员配置，创建 API Token 不会增加账号权限。

### 2. 在个人设置中生成 Token

1. 登录 Jenkins，点击右上角本人用户名，进入 **Security / 安全**；较旧版本入口可能叫 **Configure / 配置**。
2. 找到 **API Token** 区域，选择 **Add new Token / 添加新令牌**，取一个便于辨认的名称，例如 `K1FunctionReview-本机`，点击 **Generate / 生成**。
3. 在生成时复制 Token，直接保存到自己的密码管理器或下述本地配置文件；新式 Token 后续无法再次查看明文。不要把 Token 发到聊天、截图、终端参数或 Git。
4. 记录该 Token 所属账号的真实 Jenkins 用户 ID，作为 `username`，不能用昵称或显示名代替。个人测试实例归属也使用这个字段。

入口及用户名 + API Token 的认证方式见 [Jenkins 官方认证说明](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)，Token 管理见 [Jenkins 官方 Token 说明](https://www.jenkins.io/blog/2018/07/02/new-api-token-system/)。找不到 Token 区域或禁止创建时联系管理员，不改用他人账号、账号密码或 Job 的远程触发 Token。

### 3. 复制空模板，在本机填写

建议将凭证文件放在仓库外。下面在用户目录创建私有配置，存在时保留原文件；在 FunctionPreview 根目录执行：

```powershell
Set-Location C:/Project/FunctionPreview
$jenkinsConfig = Join-Path $env:USERPROFILE '.config/k1-function-review/jenkins.local.json'
if (-not (Test-Path -LiteralPath $jenkinsConfig)) {
    New-Item -ItemType Directory -Path (Split-Path $jenkinsConfig) -Force | Out-Null
    Copy-Item -LiteralPath './review-k1-function/assets/jenkins-local-config.example.json' -Destination $jenkinsConfig -ErrorAction Stop
}
notepad.exe $jenkinsConfig
```

在本地编辑器填写并保存为 UTF-8 JSON（无 BOM、无注释）。不在终端运行显示整个配置文件的命令。字段按下表取得：

| 字段 | 填写方式 |
|---|---|
| `baseUrl` | 维护者提供的 Jenkins 根地址，包含实际上下文路径（如部署在 `/jenkins` 则保留它）；不要填某个 Job/Build 页面、登录页，也不要附带账号、密码或查询参数 |
| `username` | Token 所属的本人 Jenkins 用户 ID，同时用于个人测试实例归属 |
| `apiToken` | 上一步新生成的个人 API Token；空模板没有可用凭证 |
| `deploymentDefaults.ALIVE` | 模板默认 `"5"`；实际单位和可用值以当前 Job 参数说明为准 |
| `environmentWorkflow.groupId` | 已确认通知消息的 `openConversationId` |
| `environmentWorkflow.sender` | 已确认备份机器人的消息字段 `sender` |
| `environmentWorkflow.senderId` | 同一机器人的消息字段 `senderOpenDingTalkId`，不是群 ID 或显示名 |
| `environmentWorkflow.runtimeHost` | 维护者确认的个人测试部署节点，须与实际部署和 `k1-mcp.ssh_exec` 探针目标一致，不从 MCP URL 推测 |

保持文件仅本人及必要的本机管理员可读，不放入共享/同步目录。本文使用仓库外位置，每次调用脚本都传 `--config`；如果使用默认 `C:/Project/K1Game/.jenkins.local.json`，同样不能提交该文件或覆盖已有配置。DownKey 留给每轮备份获取，不写进这里。

### 4. 只读验证并维护 Token

在同一 PowerShell 中执行，或先重新设置上一步的 `$jenkinsConfig`：

```powershell
python -X utf8 ./review-k1-function/scripts/jenkins_test_environment.py inspect --config $jenkinsConfig
```

通过标准：返回目标“自定义代码配表分支启动个人远程服”的任务信息与参数定义，不出现 `error`。此 `inspect` 只发送读取请求，不触发构建；它只验证该部署入口的读取能力，不能证明备份/下游任务权限、构建权限或整套环境已就绪。另由维护者确认其余任务权限，再按环境流程进行已授权的操作。

- `JENKINS_HTTP_401` / `403`：核对用户名与 Token 是否属于同一账号、Token 是否撤销、任务权限及代理策略；Jenkins 认证失败也可能返回 403，不能一律理解为“Token 正确但无权限”。
- `JENKINS_HTTP_404`：核对根地址、上下文路径和当前 Job 路径；部分权限配置也可能隐藏任务。
- `JENKINS_NETWORK_ERROR`、重定向状态或 `JENKINS_INVALID_JSON`：检查内网、证书信任、代理/SSO 是否返回登录页面。应修正入口或管理员配置，不关闭 TLS 验证来绕过问题。
- Token 丢失或泄露：在本人 API Token 页面撤销对应 Token，生成新的 Token 后更新本地文件，并再次执行 `inspect`。不要把新旧 Token 或配置差异提交到 GitHub。

## 本地配置模板

分享包提供无凭证模板 [assets/jenkins-local-config.example.json](../assets/jenkins-local-config.example.json)。接收者复制到自己的默认配置位置或其他私有位置，再在本地填写 `baseUrl`、`username`、`apiToken`；模板中的空值不能直接执行。不要把填写后的文件加入 Git 或分享包。

发布版的 `environmentWorkflow` 必须填写 `groupId`、`sender`、`senderId`、`runtimeHost`。本仓库不预填内部群、机器人身份或测试节点；由接收者先只读确认，再写入自己的本地配置。这些是环境标识，不是访问密钥，填写标识不会自动获得权限。

## 运行环境与目录

- 当前使用路径为 Windows：本地 Python **3.10 或以上**、可调用的 `powershell`、Git。需要读取 LFS 工作簿时还需 Git LFS。备份部署脚本使用 Python 标准库；正式 Excel 解析与 `acceptance/config_variants.py` 需要 `openpyxl`。`pytest`、skill 校验使用的 `PyYAML` 只在开发/验证 skill 时需要。
- 自动建环境另需 DWS CLI、Node.js、mcporter；命令应可被当前进程发现。当前 Windows 适配器会寻找 mcporter 安装目录下的 `node_modules/mcporter/dist/cli.js`，可先核验入口存在；不兼容的安装布局须适配后再运行。
- 远程测试节点需可用的 `python3`（当前探针使用 Python 3.6+ 标准库）、Docker CLI 和前述读取权限。仅本地安装 Docker 不能替代远程节点权限。
- 源码目录约定为 `C:/Project/K1Client/k1_client`、`C:/Project/K1Game/game`、`C:/Project/K1Dataconfig/dataconfig`，各自存在可用的 `origin`。仅部署环境需要 server/config 两端；完整审核按三端准备。
- 默认项目位置为 `C:/Project/FunctionPreview`，skill 位于其中的 `review-k1-function/`。脚本包含固定 K1 仓库路径、由脚本位置推导的项目根目录和写入边界，**不是复制到任意 skills 目录就能直接运行的通用包**。接收者可按此布局放置项目，再把 skill 注册/链接到自己的 skills 目录；不同目录或平台需同时适配脚本、合同和验证，不能只改说明中的路径。
- 分享完整 `review-k1-function/` 与 `slg-testcase-generator/` 实体内容，包括各自的 `SKILL.md`、脚本、引用和资源。本机安装入口是 Junction，不能只发这个链接，也不能只发 `SKILL.md`。若分享整个 FunctionPreview 项目，不包括 `.tmp`、`.cache`、`reports` 和用户配置；运行记录可能含内部数据与访问定位。

## 首次使用的提示与只读检查

先按本次任务给接收者一份简短清单：**必需依赖、已检测项、缺失项、凭证应在哪本地配置**。凭证只核对必填字段是否存在且非空；不显示值，不读取/输出完整 MCP 连接配置或含 token 的 URL，也不要求用户在聊天中粘贴密钥。

1. 核验完整目录和必要的外部 skill；按所选阶段检查 `python`、`powershell`、`git`、`dws`、`node`、`mcporter` 可执行文件及需要的库。
2. 核验个人 Jenkins 配置存在、DWS 已登录、Git 凭证已就绪、mcporter 能找到 `k1-mcp.ssh_exec`。只报告连接名、登录/可用状态与缺口。
3. 使用 `jenkins_test_environment.py inspect --config <本地配置>` 只读检查 Jenkins；按需要通过现有适配器只读验证消息来源与测试节点。群消息可能包含 DownKey，不把原始 DWS 输出写进聊天或报告。
4. 只读检查成功不等于具备 Jenkins 构建权限。缺权限/连接时明确说明对应阶段不可执行，并继续不依赖它的部分；不要为“试权限”触发构建，也不要因缺少 Unity、Word 等无关依赖阻塞单独部署任务。

依赖齐备且操作范围已有授权后，按 [jenkins-test-environment.md](jenkins-test-environment.md) 执行原流程，无需重复批准同一范围。

## 发布版 Unity 模板

`assets/acceptance/unity/gold-miner-adapter.json` 不包含真实账号、活动、会话、程序集绑定或过去的验证结果。使用前核验实际源码 SHA/文件哈希并读取当前 Unity 身份，将模板另存到本机的私有运行目录；保留空值时不可直接执行。
