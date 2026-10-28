# macOS 安装与首次配置

本文是 [外部依赖与首次配置](dependencies-and-setup.md) 的 macOS 对照版。依赖范围、凭证要求、只读验证标准和安全约束与 Windows 版相同，这里只列出 macOS 上不同的命令与路径；未提及的步骤按原文执行。

## 路径约定

| 项目 | Windows | macOS |
|---|---|---|
| K1 根目录 | 用户提供的工程根目录 | 用户提供的工程根目录 |
| Client | `<K1根目录>/K1Client/k1_client` | `<K1根目录>/K1Client/k1_client` |
| Server | `<K1根目录>/K1Game/game` | `<K1根目录>/K1Game/game` |
| Config | `<K1根目录>/K1Dataconfig/dataconfig` | `<K1根目录>/K1Dataconfig/dataconfig` |
| Jenkins 配置 | `<K1根目录>/K1Game/.jenkins.local.json` 或 `--config` | `<K1根目录>/K1Game/.jenkins.local.json` 或 `--config` |
| 推荐私有配置 | `%USERPROFILE%/.config/k1-function-review/jenkins.local.json` | `~/.config/k1-function-review/jenkins.local.json` |
| DWS 二进制 | `~/.local/bin/dws.exe` | `~/.local/bin/dws` |
| PowerShell | `powershell`（5.1） | `pwsh`（PowerShell 7） |

每轮先取得用户本轮明确提供的 K1 工程根目录；只有用户本轮明确要求沿用此前已确认路径时才可复用。不能从默认目录或环境变量自行决定。核验三端目录后，将此路径作为 `K1_PROJECT_ROOT` 传给本轮 Python 与 PowerShell 脚本进程；不要为此改写 `~/.zshrc`。FunctionPreview 项目根目录仍由脚本位置推导，`.cache`、`.tmp`、`reports` 写入边界不变。

文档中其他固定路径仅为旧示例，执行时都以本轮用户提供的工程根目录或本技能所在 FunctionPreview 项目根目录替换。macOS 默认文件系统不区分大小写，与 Windows 一致，脚本中的路径比较行为不变。

## 安装基础工具

使用 [Homebrew](https://brew.sh)：

```bash
brew install powershell uv git-lfs node
brew install --cask android-platform-tools   # 仅真机路径需要 adb
git lfs install
pwsh --version
```

Python 需要 3.10 或以上。仓库 `.ps1` 脚本由 `pwsh` 执行，Python 工作流在非 Windows 上自动调用 `pwsh`。

Python 依赖（在仓库根目录执行）：

```bash
python3 -m pip install -r requirements-dev.txt -r requirements-optional.txt
python3 -m pip install -r slg-testcase-generator/requirements.txt   # 仅独立在线写表流程需要
```

## 注册 skill

macOS 使用符号链接替代 Windows Junction，把三个完整目录链接到所用 Agent 的 skills 目录（以 Claude Code 为例）：

```bash
mkdir -p ~/.claude/skills
for s in review-k1-function slg-testcase-generator jira-bug-creator; do
  ln -sfn "$PWD/$s" ~/.claude/skills/$s
done
```

已有同名 skill 时先核对来源，不要直接覆盖。

## mcporter 与 k1-mcp

```bash
nc -vz 172.20.90.39 8443            # 对应 Test-NetConnection
npm install -g mcporter@0.9.0
mcporter --version
mcporter config add k1-mcp --url http://172.20.90.39:8443 --scope home
mcporter list k1-mcp                # 须包含 ssh_exec
```

macOS 上 `mcporter` 是普通可执行文件，脚本直接调用，不需要 Windows 的 `cli.js` 入口检查。Codex / Cursor 的 MCP 配置文件位置与原文相同（`~/.codex/config.toml`、`~/.cursor/mcp.json`）。

## DWS

使用官方 shell 安装脚本，固定同一版本与单入口 skill：

```bash
curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh \
  | DWS_VERSION=v1.0.35 DWS_SKILL_MODE=mono sh
command -v dws || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
dws version --format json
dws auth login --format json
dws auth status --format json
```

通知群和机器人标识的只读核验按原文执行，用 `jq` 替代 `ConvertFrom-Json`，且不输出消息正文：

```bash
read -r "group?openConversationId: "
read -r "since?起始时间（yyyy-MM-dd HH:mm:ss，北京时间）: "
dws chat message list --group "$group" --time "$since" --limit 20 --format json \
  | jq '.result.messages[] | select(.sendType=="robot") | {openConversationId, sender, senderOpenDingTalkId, createTime}'
```

## Jenkins 配置

```bash
cfg=~/.config/k1-function-review/jenkins.local.json
mkdir -p "$(dirname "$cfg")"
[ -e "$cfg" ] || cp review-k1-function/assets/jenkins-local-config.example.json "$cfg"
chmod 600 "$cfg"
open -e "$cfg"
python3 -X utf8 review-k1-function/scripts/jenkins_test_environment.py inspect --config "$cfg"
```

字段说明、通过标准与错误码处理与原文相同。

## jira-bug-creator

```bash
uv run --script jira-bug-creator/scripts/submit_from_json.py /path/to/bug.json
```

## 本地验证

```bash
python3 -m pytest tests slg-testcase-generator/tests -q
```
