# 巨蛇四期运行脚本说明

归属：`k1-giant-snake-phase4`；[功能档案](../experience.md)。整理日期：2026-11-03，Asia/Shanghai；2026-11-04 S-04（client 4177b094）复用fastlogin/observer/beam-probe/esc并新增两条模板，均已在S-04实际执行。来源：S-02（`FunctionPreview/.tmp/k1-nk10652-20261103-unity`，client `dev_NK-10652@21cf159`，Unity 2022.3.62f2c1 / OSXEditor）。

`.cs.txt` 是 Unity MCP `execute_code`（`action=execute`，Roslyn）的方法体片段，不是独立程序；全部用反射访问游戏类型（编译上下文不引用 `Unity.Entities` 与业务程序集）。`.sh.txt` 是 macOS zsh 模板，通过 `mcporter call --http-url http://127.0.0.1:8080/mcp --allow-http execute_code` 调用。使用前复制到本轮 `.tmp/<run-id>/`，替换占位符并核对当前源码签名；模板保存、本轮执行与业务验收是不同层级。

| scriptId | 文件 | 用途 | SHA256 | 只读/写入 | 完成信号与停止 |
|---|---|---|---|---|---|
| phase4-ecs-probe | `phase4-ecs-probe.cs.txt` | 读取 `World.I.LogicMgr` 的 `Phase4SwarmBulletComponent`（位置/航点/Leg/Elapsed）与 `Phase4RingWaveComponent`（半径/回流/追加/圆心），并输出 World.IsPaused | f9cc18e2cb5d52f35f23659e1ea6d722b6849807c5a12d2b9d62cefb9e24cf98 | 只读 | 单次返回一行；按需循环采样 |
| phase4-hit-ledger | `phase4-hit-ledger-probe.cs.txt` | 经 `SystemAPI.QueryEntities<T>` 结构体枚举器（反射 GetEnumerator/MoveNext/Current）统计 `Phase4SwarmHitComponent`、`Phase4RingHitComponent` 记录数与唯一（弹体/波,目标）对 | c8e5010faa4a22ba9092d843c51b841f0ad07b456f385288629535d4a5a578ab | 只读 | 单次一行 |
| dragon-segment-count | `dragon-segment-count.cs.txt` | 统计存活 `DragonUnitMoveComponent` 实体数、ID 和与路径进度 T 的最大/平均值，用于复活前后“不复生/整体后退”比对 | a164cebefb4e0deeeb10d2ccabe3307cecaf971cad416f9e25afbc4cc5590509 | 只读 | 单次一行 |
| phase4-beam-probe | `phase4-beam-probe.cs.txt` | 读取 `Phase4BeamRuntime.Active.m_Casts` 每个 cast 的 Slots 数与 hitVisuals（束数核对） | 95d3b78c65def029105a1ec15bc023358d91ca91fb10ebb5e108529a09e9a4ef | 只读 | 单次一行 |
| battle-observer-tick | `battle-observer-tick.cs.txt` | 战斗观察单步：记录进度/关卡；选卡默认点第一项、关闭触发礼包/技能页/奖励列表；遇到未知弹窗或结算返回 stop | eb6ea82224cfd0729901780be67f01889a28e58242b5031adb4a814319e61cfd（S-04：忽略列表加入ui4109Widgets，否则第41关被误判为未知弹窗停止） | 写（正常UI点击） | `stop=true` 时停止，人工处理弹窗 |
| esc-keyback-step | `esc-keyback-step.cs.txt` | 记录状态→截图→调用 `Main.SimulateKeyBack()`（ESC/返回键同一处理）→再记录；`__TAG__`、`__EVIDENCE_DIR__` 需替换 | 1d4c76d45cc87ee872c0d385845d3a0224a45a6bcec3484ca1cedd6caa96fb53 | 写（等同按返回键） | 立即返回；+3 秒再取状态 |
| fastlogin-dev | `fastlogin-dev.sh.txt` | 登录页 GM 快速登录：打开 `FastLogion` 面板→勾 Dev→填 PlayerId/ServerId→**面板内** CloseBtn→点“我的服务器”角色条目→确认 `UISwitchRole`→等待 LPlayer 身份 | 146537319a63af67d748c34e3540c6c79924460a20d789d413b72ce3eaa80553 | 写（登录） | 输出 `identity: <pid>@<sid>` |
| enhance-card-ids | `enhance-card-ids.cs.txt` | 经DeepUI.PopupManager.FindPopup(UI.UIEnhanceCard)读取m_EnhanceCardIds与卡名/描述，用于按选项ID找特定强化卡（如111020617）并核对多语言文案 | 196b5f39b5e26af77db2889ed3cf11a55ceda56b35ee85d5731109519ff7341b | 只读 | 返回`no popup`或一行ids+文本 |
| esc-when-hud-clear | `esc-when-hud-clear.cs.txt` | 仅在无选卡/礼包/结算弹窗时截图（`__EVIDENCE_PNG__`替换为绝对路径）并调用Main.SimulateKeyBack；有弹窗返回busy，配合observer循环使用 | 494138e3a23c12afe1d7293ea317b3c53977811f7a6e316530ce2ce8cca1aaf5 | 写（等同按返回键） | 返回`esc sent`后1–2秒用暂停页是否出现判定，未出现则重试（见RUN-ESC-AFTER-CARD） |

参数：`__PLAYER_ID__`、`__SERVER_ID__`（本轮授权的测试账号与专属服）、`__ROLE_NAME__`（“我的服务器”列表中该服的设备角色条目名），身份与授权每轮重核，不沿用历史值。

注意事项（均为 S-02 实测）：
- `CloseBtn` 必须在 `FastLogionPanel` 内查找；在整个 UILogin 中 First 会命中登录弹窗自身关闭键，导致登录卡在 79%。
- 截图用 `ScreenCapture.CaptureScreenshot(<绝对路径>)` 写入 `.tmp`；MCP `manage_camera screenshot` 默认写工程 `Assets/Screenshots`，会弄脏客户端仓库。文件异步落盘，记录证据前稍等 1–2 秒。
- Unity 控制台经 MCP `read_console` 读不到 ExLog 输出，协议与飘字从 `~/Library/Logs/Unity/Editor.log` 按时间戳截取。
- `execute_code` 返回值勿用 `dynamic`（缺 Microsoft.CSharp 绑定）；不要返回未完成 Task（见 TOOL-ASYNC-REFLECTION）。
- 观察器只做正常界面点击，不替代业务判断；选卡策略固定“第一项”，不代表策略最优。
