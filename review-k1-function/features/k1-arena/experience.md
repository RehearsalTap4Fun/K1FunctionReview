# 竞技场：验收经验档案

featureId：`k1-arena`。关联：NK-10402 / dev_NK-10402（2026-10-27 历史）；NK-10371、NK-10459（599 表第 32/33 项，仅已发 MR、未合入 dev，本轮排除）。更新：2026-10-29（Asia/Shanghai）。10/27 Unity 21 项的 18 通过、3 失败（2 问题）仅属历史批次；10/29 误纳入两项的实测只保留开发参考，不计 599 本轮通过或失败，真机未执行。

## 再次验收先看

竞技场本服与跨服开关分别为 D2SwitchCfg 354、355。服务器部署成功后，还需核对进程、心跳、实际加载配置、Arena 阶段及客户端实际 SID；Jenkins 成功不等于业务通过。历史服务器、账号和 GM 授权不继承。

## documentBaseline

- status：needs_review。
- source：https://jira.tap4fun.com/browse/NK-10402 。
- currentVersion：本轮原文回读及内容保存在来源 S1；不以时间戳代替文档版本。
- checkedAt：2026-10-27 15:35 +08:00。
- reason：第 5、6.1 条已按用户决定更新；机器人首次刷新规则与历史确认的“首次参战前”口径须保留差异。第 6.2 条浮点要求与当前整数类型不一致，尚未形成完整运行结论。
- nextAction：沿本轮决定与原文核对受影响规则，继续独立业务用例；不得直接标为文档全部确认或功能通过。

## 来源与版本

原始证据不随 Skill 分发，缺失时需重新核对。

| 来源 | 版本 / 层级 | 定位 |
|---|---|---|
| S1 | 2026-10-27 原文及静态材料 | FunctionPreview/.tmp/nk10402-20261027-preflight/requirements-readback.json、matchslot-type-evidence.json |
| S2 | server 27322ad26e595d85501a1c3536a6dbf8820468c8；config d79bc46ed71dfd91e48189d812dce8b7def3cb7d；部署与加载验证 | 同批次 merge-dev-result.json、server-runtime-probe.json、server-loaded-config.json |
| S3 | client 9812b8bc2d757222a8a56b9e002bd660ccab089a；转换及物化，未证明客户端已加载 | 同批次 conversion-receipt-v2.json、client-materialize.json |
| S4 | Unity 2022.3.62f2c1 首次启动排障 | 同批次 unity-launch-v2.json、unity-isolated-v2.log |

## 已验证方法和待验证事项

| entryId | 方法 / 结论 | 状态、范围及下次动作 | 来源 / 日期 |
|---|---|---|---|
| arena-switch-layer | cfgshow D2SwitchCfg 354,355 可读取服务端已加载行；必须分别检查 ServerSwitch、DevStatus 的目标 SID 范围 | 已验证读取；客户端 SwitchOpenNtf 仍需独立取证 | S2 / 2026-10-27 |
| arena-custom-slot | cfgshow NewArenaMatchSlotCfg 返回实际自定义组，不能只看基础表；本批加载 custom/10 的五档 | 已验证读取；每轮重新绑定分组与正式 XLSX | S2 / 2026-10-27 |
| arena-stage | arenastage show 返回阶段及覆盖设置 | 已验证读取；不将 show 结果当作已能进入竞技场 | S2 / 2026-10-27 |
| arena-config-compat | 老工单配置缺少 dev 新表和生成器接口，可能同时导致服务端配置启动失败及客户端 CfgG CS0535；本批合入 dev 后转换和部署恢复 | 已验证本批修复环境；正式表冲突及工单内容保留仍需逐次核对 | S2、S3 / 2026-10-27 |
| arena-gap-type | 正式 NewArena / custom 10 表的 GapMin/GapMax 为 int；服务端字段与取值函数为 int32，与工单第 6.2 条浮点要求不同 | 已验证静态差异；不冒充游戏内复现，也不擅自改需求或代码 | S1 / 2026-10-27 |
| unity-upm-allusersprofile | Windows 子进程缺 ALLUSERSPROFILE 时，UPM getGlobalConfigRoot 的 path.join 会报路径参数 undefined；仅对本轮 Unity 子进程设置为 ProgramData 后安装包成功 | 已验证本机启动方法；先查日志和子进程环境，不持久修改系统变量 | S4 / 2026-10-27 |
| unity-invoke-task | 通过 EditorDebugMCP 反射调用 StartAsync 并直接返回 Task 后，编辑器无响应。源码显示请求和 JSON 序列化在主线程，存在读取未完成 Task.Result 的死锁风险 | 无响应已观察；死锁机制为源码推断，未取线程转储。恢复经用户确认重启。后续只返回 IsCompleted 等简单状态，或用已连接 MCP 的 execute_code 启动异步任务 | 同批次 unity-invoke-incident.json / 2026-10-27 |
| arena-gm-scope | changeswitch 虽注册为 player 命令，实际修改服务器全局开关；arenainfo 会调用 ArenaEnsure，并非严格无副作用查询 | 静态确认作用域；调用前绑定本轮授权服务器和角色，保存前后证据 | S2 对应源码 / 2026-10-27 |

## 业务入口、界面与反馈

客户端 Logic.LoginMgrNew 与 K1D2Config 提供开发登录入口；本轮在用户现有 dev Unity 中完成正常角色创建、已有角色切换与竞技场业务验证。已覆盖快照、重复挑战、连续刷新、分档及边界/降档、全榜取人、扣分与激活重置、积分结算、消耗异常和真实 ESC 返回/重进。战力补位的未参战过滤失败；MatchSlot浮点要求仍为静态差异。用户限定 Unity，不能推导真机通过。本轮没有新增界面布局/文案要求，未扩展三语布局验收，依据见私有 ui-applicability.md。

反馈表来源、实际列映射、权限与版本状态仅保存在本轮私有运行目录；不得用版本“不进当前版本”替代开发验收结论。截图和在线附件未取得时保持缺口。

## 脚本、归档与更新

暂无已完整走通、可分享的业务操作脚本。带本轮环境绑定的探针仅留私有运行目录。当前证据仍被补验计划引用，未进行过程文件清理。

2026-10-27 新建档案，记录 S1–S4 的环境方法与静态差异；本轮运行计划仍在执行。

## 2026-10-27 业务实测增量与版本中断

- 使用现有 Unity MCP 的 execute_code 启动 UniTask 并 Forget，结果写本轮私有回执，立即返回简单值。ScreenCapture.CaptureScreenshot 可取得实际 Game View，截图不依赖 Computer Use。不要直接返回未完成异步对象。
- arenaunlock 仅满足某旧进度字段时，不保证当前客户端 Rogue 解锁条件同步；先核对当前入口使用的最大通关层数，必要前置用已经授权的前进关卡 GM。此操作可能发进度奖励，不用于回退恢复。
- 正常防守阵容请求与挑战报告能验证列表生成时的快照。对手 GM 变阵后，既有列表仍保留原阵容，正常重新登录后亦可读取同一快照。原始 BattleReport 的派生属性未初始化时不可用 IsBattleWin，核对协议 isAtkWin 与 atk/def。
- 对手候选会排除紧邻上一批；真人总数少并不能证明“有足够可用真人仍强制机器人”。补验至少准备可交替的完整分档样本池。
- 本轮未参战样本连续正常败守 1000→996→993，数据库最终确认 joinedweekts=0、defendlosecount=2。PlayerSaveDura 为五分钟、分批落盘；即时 Mongo 旧值不能直接判为持久化丢失。
- 17:01 后专属服被另一 Jenkins 部署改成 dev 服务端与 NK-10371 配置。检测后停止测试写操作，历史回执按版本保留；变更后观察到的激活重置不能计入原工单通过。滚动环境探针不得覆盖历史结果唯一版本依据，GM 前置同时校验 SID、容器所有者、镜像与探针时间。
- 原始回执、身份绑定脚本、截图和版本漂移记录仅保存在本批 FunctionPreview 私有目录。完整验收与反馈附件尚未闭环，不清理仍被台账引用的证据。

## 2026-10-27 收尾增量

- 用户批准恢复后，Jenkins 12097/11576 恢复相同冻结服务端和配置。当前 Unity PID50188 未新增实例、转换文件未提交。
- 分档真人充足时4次刷新均1高2中2低；闭区间各端点实际入选。自身第58名匹配到第1名，差57名，证实本批不受旧上下50名限制。正常刷新免费次数与5/10/20再每次+10的付费梯度、资源不足与挑战耗尽已核对。
- 确定运行问题：补位目标正常参战后仍被战力补位选中。服务端日志证明积分候选池为空、命中weak-tail路径；冻结代码没有JoinedThisWeek过滤。影响2个断言，计1个缺陷。后第10名实际入选；后第11名14次随机刷新未入选只作有限样本观察，不能扩大为穷尽证明。
- 正常角色登录后首次ArenaQuery将被扣分陪练重置1000，随后GM只用于读回。读取型arenainfo会ArenaEnsure，因此不能在激活前用它验证“仍未重置”，避免查询改变前置。
- 服务器重启后同步玩家GM可能返回offline or error；本批setroguelvl是已核对的异步玩家命令，可先加载本轮角色并推进必要进度，再做阵容前置。不泛化为随意加载/修改其他角色。
- GameView.SendEvent(KeyDown Escape)返回handled但没有触发游戏Input.GetKeyDown，本批未将其算产品失败。实际ESC使用Computer Use向唯一现有Unity窗口发送，列表、叠加弹窗、主页面均返回，正常重进成功；业务操作和截图依旧MCP。
- 版本表G17最终备注写入并回读，保留其他值/公式和版本状态。独立完整QA反馈表、在线问题附件未闭环，不声称已附图；本地后台证据完整保留。
- 当前原始证据、计划、身份绑定脚本和截图均仍有验收/复验依赖，本轮未删除。后续针对2处问题修复后复验，不擅自改代码或需求。

## 2026-10-29：原599第32/33项误纳入后的开发参考实测（范围已排除）

范围更正（2026-10-29）：用户明确版本日只验收已合入 dev 的进包项；fresh 原表核实 NK-10371（原第 32 项）与 NK-10459（原第 33 项）仅已发 MR、尚未合入 dev，两项此前被误纳入本轮。因此全部相关后续验收已停止；已发生的 Unity 实测、截图、协议和方法仅作开发参考，不计 599 本轮通过或失败，不当作 599 已进包缺陷，不移挂其他正式项，也不扩报第三个扣分问题。下列已验证只表示所列技术操作/现象在当时环境有证据，不能证明尚未合入目标 MR 的实现结论。历史 entryId 和 S599 来源编号保留为可追溯标识，不表示本期范围。

### 开发参考来源与当时运行版本

下列定位均在私有 `FunctionPreview/.tmp/k1-599-supplement-20261029/`（简称 R），不随 Skill 分发；角色、账户缓存、设备标识、登录令牌、原反馈表链接及分配信息只留私有索引。具体服务器和 GM 授权必须每轮重新绑定。

| 来源 | 日期、层级和范围 | 私有定位 |
|---|---|---|
| S599-A | 2026-10-29，冻结版本与 Unity 单次 NPC 实战；不是本项全部规则通过 | `manifest-after-conversion.json`；`arena-child/receipt32-main-one-npc-partial.json`、`battle-manager-actual.json`、`battle-observer.jsonl` |
| S599-B | 2026-10-29，EN→AR→RU 普通切语、受影响可见 UI、两处 UI 缺陷 | `arena-languages/three-language-partial-receipt.json`、`ui-issues-independent-receipt.json`、各语言原图/状态 JSON；`ru-main-countdown-geometry.json` |
| S599-C | 2026-10-29，自控防守角色合法组阵、真实详情 Ack、旧候选复查及首次真人战报；仅采用下表列出的两项事实 | `p2-lineup-fixture/fixture-receipt.json`；`arena-root/own-p2-old-defense-actual.json`、`own-p2-same-candidate-defense-after-edit.json`、`own-p2-first-settlement-actual.json`；`arena-p2-edit/fixture-only-receipt.json` |
| S599-D | 2026-10-29，原表多图落位、逐图在线打开与回读 | `feedback-images-32/final-image-verification.json`、`feedback-images-33/final-image-verification.json`；截图和非图片列差分同目录 |
| S599-E | 2026-10-29，同一 SDK 账户已有角色顺序切换的私有恢复守卫，不是共享业务操作脚本 | `backend/login-existing-p1-after-p2.cs.txt`、对应离线证明/登录回执；敏感缓存快照不随 Skill 分发 |
| S599-F | 2026-10-29，后续受限 EN 单次弱 NPC 挑战与自然积分样本；非真人业务通过 | `arena-p2-en-npc/receipt-en-p2-npc-partial.json`、`protocol-challenge-and-assets.json`、`en-p2-settlement-stable-readback.json`、`actual-asset-score-delta.json`、`final-handoff-readback.json` |

S599-A manifest 的冻结输入：client `f19a56c9d7dda8b1a4ba726d024e5b0512a24168`、server `242b2db3eb2a3d206a17e491da7ed4283dbce235`、config `f904ffa7a7a9dc55f5173e71b7a3ed3216ffd263`。磁盘物化与运行时实际加载仍分开举证，不能只凭 manifest 宣称已加载。

### 保留的技术经验（实际观察日均为 2026-10-29，599 范围已排除）

| entryId | 结论 / 方法与状态 | 适用边界、成功信号及下次动作 | 来源 |
|---|---|---|---|
| arena599-normal-ui-route | 已验证普通 HUD `GameModeButton`→实际已解锁 NewArena 项→既有 `NewArenaUIUtil.TryOpenMainPanel`；既有主榜按钮进入候选、规则、记录、日/周奖励预览。真实注册 `EventTriggerListener.onClick` 优先于可能为空的 Button.onClick | 导航必须保留解锁/首次视频/生命周期；本次首次视频自然结束，未冒称实际按了 skip。组阵 fixture 的直接入口不能记为普通 Arena 入口通过。未知覆盖先看图与类型，实际推广层用其正常 CloseBtn；关闭重进后再取干净证据 | S599-A/B |
| arena599-language-panel-relogin | 已验证现有语言选择面板的目标语言行/Toggle 与注册点击→正常确认→产品正常重启重登；按 EN→AR→RU 集中检查主榜、规则、记录、候选及日/周奖励，结束恢复 RU | 切语前后守卫实际角色与缓存已有角色，不能直写语言缓存。三语独立 UI 阶段未挑战/刷新/购买，次数和免费刷新保持前态；后续独立 EN 实战见 S599-F。RU 规则文字超出首屏但可正常 ScrollRect 拖动看到尾部，不把可滚动正文当裁切错误 | S599-B |
| arena599-typed-ack-evidence | 已验证按实际协议类型保存运行数据：详情 `cspb.ArenaV2DefenseLineupAck`，挑战 `LNewArenaMgr.LastChallengeResult` 的 `ArenaV2ChallengeAck` 及 `BattleReport`；普通组阵捕获 `LineupBuildHeroAck.errCode=0` 与 `LineupsNtf` | 绑定目标身份、errCode、teamID、heroCfgID/level/star、实际数据增量。观察器文件为空只能说明该观察器未捕获，不能推断业务无回包；真实已解码 mgr 缓存是运行证据，但不冒充原始网络 trace。异步请求只启动后返回简单状态，不返回未完成 Task | S599-A/C/F |
| arena599-npc-runtime-sample | 已验证 RU 与后续 EN 各一场独立普通弱 NPC 挑战、真实战斗/结算和普通关闭返回：各自积分 1000→1006、次数 5→4，结算 +6 为 `#9BFF96`；实际碰撞特效画面与两路 AudioSource playing 留证 | 声音是实际播放状态采样，未称人耳试听。主/辅实际音量 1/0.6 只是观测值，不代替目标配置符合性结论。NPC 对手不显示分差，不能验证负分颜色；最初 HUD 打开截图仍在 Loading，真实战斗证据使用实际碰撞图。任务计数需核当前激活任务与权威前后态，空客户端任务缓存不等于服务端无任务 | S599-A/F |
| arena599-ar-weekly-tab-mirror | 开发参考现象：AR 奖励初始日页的页签字形可读，正常点周页后两个页签文字水平镜像，标题/正文未同步异常 | 技术记录键 `arena-reward-ar-tab-mirrored-after-weekly`，来源为误纳入的原第 32 项；只作开发参考，不移挂其他正式项。周页实际 Ack 为 typ2/errCode0；问题图在点击 RPC 完成约 0.897 秒后采样，没有额外五秒稳态或 lossyScale/rect 证据，不能扩大为已证明长期持续或已确认根因；下次补稳定帧/变换取证及修复复验 | S599-B/D |
| arena599-ru-daily-countdown-clip | 开发参考现象：RU 主榜底部每日倒计时仅显示长文案，数字换行后被截掉 | 技术记录键 `arena-main-ru-daily-countdown-truncated`，只作开发参考，不计 599 问题。运行 `txtDailyTips` 含完整时间，font32、Wrap+Truncate、rect800×60、preferredHeight120、visibleCharacterCount38；EN/AR 数字可见。不得将此与可滚动规则正文混为同一问题；下次正常重进复验实际数字可见 | S599-B/D |
| arena599-defense-card-prefab-label | 开发参考卡片显示现象：实际详情 Ack 中自控英雄 level1/star0，卡片仍显示 prefab 的 `LV.9` | 只记录实际协议与原图不符，不用卡面数字反推英雄真实等级。首次旧队与后续第二队图均见该标签；下次同类型详情检查实际 level/star 绑定及刷新生命周期 | S599-C/D |
| arena599-search-snapshot-divergence | 开发参考观察：当时冻结 dev 的实测与 10/27 历史不同：首次详情为 team1；对手合法变阵后，未刷新原候选，详情变成 team2，首次真实挑战报告防守方也为 team2 | 原候选列表/刷新时刻/匹配轮次等权威前态未变有私有证据，不能以重登或新详情请求当成重新搜索。共享档案只保留当时搜索快照未保留的技术事实；目标 MR 未合入，不能记为599已进包问题。真人重复挑战、扣分/激活与原第7条相关后续均已停止，不能据结算单图扩报第三项问题 | S599-C |
| arena599-private-role-switch | 同一 SDK 账户的自控角色切换已通过完整 StopPlay→核旧角离线（必要已授权踢旧自控角）→新 Play→正常选择现有缓存角色及 LoginAck 的私有守卫方式恢复 | 仅保留方法摘要；具体角色、账户、设备标识、缓存路径/内容与 token 不共享。必须每次重新核 SDK 所属、离线证明新鲜度和目标身份；不让两个角色同时在线误触发开服或提前进入 Arena。未参战样本先从普通编队 fixture 准备自有英雄，进入 ArenaQuery 会破坏激活前态 | S599-C/E |
| arena599-k-cell-multiimage-dom | 已验证无需原生 CUA 的多图回填：按稳定 Jira fresh 定位行和问题截图列；空单元格首图可用 MCP 附件上传凭据/返回地址上传后 DWS write-image；已有图绝不能用该替换命令 | 选目标地址→表格编辑 textarea 正常 `F2` 打开图片 popover→“上传图片”前启动 filechooser→单文件一次追加；读实际 `div[src]` 缩略图并逐图正常点击在线预览，确认 img.complete 与原始 naturalWidth/naturalHeight，保存页面截图后实际查看。此轮原图为1080×1920，其他图按实际尺寸核对。保留全部旧资源、已保存状态和非图片列回读差分；上传结果未知先查资源/回执，禁止盲目再传。工具连接重置可重绑现有标签页，不重传已成功图片 | S599-D |
| arena599-escape-input-boundary | 当时桌面焦点未交付游戏 Input，真实 ESC 留有输入能力 blocked 记录；现两项已排除，不继续重试 | 10/27 真实 ESC 通过不能移植本轮。GameView.SendEvent/模拟返回结果不冒充真实键盘；也不能将输入未送达写成游戏返回失败。将来功能重新进入已确认范围时，才按当轮输入能力与授权重新判断 | S599-A/B |

### 范围更正后的停止状态与证据留存

- 原第32/33项仅已发MR、未合入dev，本轮均排除。任何旧partial/failed回执仅保留当时事实，必须与本范围更正一起读取，不进入本轮验收统计。
- RU/EN各单次NPC、三语可见UI、AR周页签/RU倒计时、level1/star0与卡面LV.9、旧候选team1变team2及真实战报均保留为开发参考；不迁移成其他正式项的缺陷。
- 当时任务适用性/增量、目标声画参数、真人重复/负分、原第7条及被动扣分/激活等未闭环内容保留未知，不继续执行、不制造第三扣分问题。将来目标MR真正合入后，应重新确认需求/版本/运行范围，技术方法可复核复用，历史结果不得直接继承。
- 用户当时仅允许Unity，真机未执行；已有ESC输入能力blocked属于当时环境记录，不能算本轮业务失败。
- 已附原图和逐图在线预览证据全部保留，不删除线上K或原始文件。线上F/L状态恢复与更正通知由主验收者负责；本次档案更正没有操作线上字段、图片、通知、Unity或GM。
- 身份绑定脚本、私有登录守卫、运行探针、typed Ack、原图及台账仍保留依赖；不删除。私有 `R/arena-experience-archive-20261029/scope-correction.json` 保存fresh来源哈希、范围覆盖清单及共享档案写前/写后哈希，后续读取须优先应用此更正。

当时 EN 独立实战（S599-F，仅开发参考）：正常已有角色重登后 guide 已完成且无对话，未再执行 guide GM；只挑战实际 isGuard=true/pid0 且弱于自身的一个 NPC，未刷新/购买/切角色。该场已实际捕获 `ArenaV2ChallengeAck.errCode=0` 与 `AssetNtf`，自身原 team2 保持；结算与干净 EN 主界面均实际看图，先正常关结算、等待主 Arena 恢复后再独立关闭，自有观察器清理。竞技币/药水/砖库存分别真实增加20/1/2；EXP奖励项21110101在Ack显示10，但库存及AssetNtf均为0，自动消费/封顶等语义未核实，不据此宣称丢奖。自然形成1006曾用于准备不等分排序样本；范围更正后停止该后续，不作为599通过/失败或GM加分。
