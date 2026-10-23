# 黄金矿工：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | `k1-gold-miner` |
| 名称 / 别名 | 黄金矿工 / GoldMiner / Gold Miner / 矿工活动 |
| 关联需求 / 历史分支 | NK-8062 / dev_NK-8062，仅作检索线索 |
| 档案更新时间 | 2026-10-21，Asia/Shanghai |
| 最近实际验证 | 2026-10-20 正常玩家体验；2026-10-19 反馈图核对与工具接入，范围分别见来源 |
| 维护源 | 本文件；尚未迁移在线文档空间 |

## 再次验收先看

1. 按本轮需求确认范围和版本；旧分支、SID、账号与 GM/购买许可不能直接复用。优先读下面的环境前置和历史问题，再读本次涉及的操作条目。
2. 复核正式 XLSX → 发布产物 → 客户端实际加载值 → 服务端实际配置，避免“服务端发布成功但 Unity 仍用旧配置”。
3. 固定入口确认兼容后复用；需要连续普通关操作时读 [脚本档案](scripts/usage.md)，按本轮参数安装输入辅助，再接续导航。普通关与挑战关的结果判据分开。
4. 262016 报错、同局恢复与 R13 原反馈分别核对；先查看反馈原图。历史相关性不是根因，工具输入损耗也不是玩家必需成本。
5. 阶段结束或中断时按 [经验规则](../../references/feature-experience.md) 合并新增条目，并更新 [索引](../index.md)。档案维护不刷新历史验证日期。

## 来源与版本

以下是历史定位及摘要，原始证据不随 Skill 分发。表中的本地路径相对 FunctionPreview；本机在 2026-10-21 整理时可读，分享后需核实可访问性。读不到来源时保留历史记录并将本轮适用性列为待复核，不能据摘要宣称重新验证。

| 来源ID | 日期 / 批次 | 定位 | 范围与版本边界 |
|---|---|---|---|
| GM-EV01 | 2026-10-20 / gold-miner-experience-20261020 | `.tmp/gold-miner-experience-20261020/learned-flow-validation.json`；同目录 `navigation.jsonl`、`visible-inputs.jsonl`、`learning-alerts.jsonl`、截图 | 普通 UI 操作、状态及异常；不能证明触屏命中或提速倍数 |
| GM-EV02 | 2026-10-20 / 同批次 | `reports/gold-miner-experience-20261020/experience.html`、`runtime-result.json`；`.tmp/gold-miner-experience-20261020/baseline.json` | 基线 `experience-20261020-b82528ea2`。报告只对 ENV/PLAY/GROW/PROP/CLOSE 五项体验用例标记通过；不代表黄金矿工全部策划规则或历史反馈通过 |
| GM-EV03 | 2026-10-20 | `.tmp/gold-miner-experience-20261020/version-guard-verification.json` | 输入模板错误版本拒绝安装；历史实际 UI ModuleVersionId 为 `390556e7-ff70-44fa-81b0-2e85cbee36a1`。这不是客户端/服务端 SHA 或配置版本 |
| GM-EV04 | 2026-10-20 / 开测前与就绪后 | `.tmp/gold-miner-experience-20261020/environment-gap.md`、`pre-test-baseline.json`、`ready-runtime.json`、`deployed-revisions.txt` | 配置提交 `b82528ea2a7815652846fceaf3fac2154df9de22`；开测前记录客户端本地 `a0b434ba5e7ee341abbe50efd8f209eeb118a5af`、远端 `8e04e7e616acb4263ea02691677b636bd9679221`。这些是不同观察对象，不拼成整轮最终三端版本；就绪/部署身份从对应记录回读 |
| GM-EV05 | 2026-10-13 / 14 对齐与订正 | `reports/gold-miner-alignment-20261013-01/alignment-review.md`、`confirmation-record.json`；`reports/gold-miner-source-correction-20261014/configuration-baseline.md` | 最初文档 revision 76，不代表当前文档。冻结 client `befc8f23b890fe9e3bea537496cb50003b9643fb`、server `f952961e881c1744e459b20022e4bfd7a7a4832a`、config `9cf98b07d0a9edea85521d3b21fd5be37c0c42b8` |
| GM-EV06 | 2026-10-19 / 20 | `docs/runtime-acceptance-environment-notes.md`；`reports/gold-miner-table-compact-20261019/verification.json` | 项目经验与表格核对记录；其中的后续补充需按日期区分。原反馈、在线附件和业务问题结论分别判断 |
| GM-EV07 | 2026-10-20 | `.tmp/gold-miner-experience-20261020/grab-rejection-262016.json`、`grab-rejections-all.json`、`attempts.json` | 原始异常/恢复线索；不能自动证明与 R13 相同或认定双钩根因 |

## 需求、代码与配置入口

本节是历史已核实的定位线索；当前需求和 target 最终状态需重新对齐。条目状态均为 **已验证（历史定位）**，不是本轮代码或配置正确性结论。

| entryId | 入口 | 用途及复核动作 | 验证日期 / 来源 |
|---|---|---|---|
| GM-L01 | NK-8062、dev_NK-8062、对齐记录与逐项确认 | 从本轮输入或历史记录定位原策划文档和用户决定；读当前文档，不能把 revision 76 当当前需求 | 2026-10-13/14，GM-EV05 |
| GM-L02 | `Game.GoldMiner.LGoldMinerMgr`、`GoldMinerRuntimeSession`、`GoldMinerBattleView` | 活动入口、当前会话、关卡状态及正常 UI 事件；精确文件路径在本轮冻结快照按符号定位 | 2026-10-20，GM-EV01 |
| GM-L03 | `UI.UIActivityGoldMiner`、`GoldMinerResultPanel`、`TalentPanel`、`GoldMinerRulePanel` | 主页、结算、天赋和说明页；按下表确认真实签名、生命周期与当前顶层页面 | 2026-10-20，GM-EV01 |
| GM-L04 | `ActivityGoldMiner.xlsx`；历史元素表 `MinerCoinReward` / `Revenue` / `Value` | 用 config-table-editor 只读核对正式表；按字段语义定位，不沿用旧列字母。客户端 TSV/bytes 与部署值只作对应层证据 | 2026-10-14/20，GM-EV04、GM-EV05 |
| GM-L05 | `EnterLevelAck`、`SettleAck`、`ActvGoldMinerTalentUpgradeAck` | 对应开局/恢复、结算、升级，结合 Ntf/权威状态与资产核验，不能只看 Ack 成功 | 2026-10-20，GM-EV01 |

## 环境与前置准备

| entryId | 经验与下一次操作 | 状态 / 适用条件 | 验证日期 / 来源 |
|---|---|---|---|
| GM-P01 | 开测前实际发生服务端最新关卡目标已发布、Unity 仍载入旧目标；正常导出/同步后再回读，不能在内存改目标冒充发布 | 已验证；历史配置同步问题，下次先核对各层 | 2026-10-20，GM-EV04 |
| GM-P02 | 记录初始体力/道具、天赋、关卡进度和来源；自然获取、历史库存、GM 与模拟购买分别核算。GM 体力观察原始 `Stamina`/`StaminaTs`，`CurrentStamina` 可能含自然恢复 | 已验证；既有体力夹具与体验记录，其余 GM 能力另核对 | 2026-10-19/20，GM-EV02、GM-EV06 |
| GM-P03 | 输入、日志、截图能力准备好后才开始计时玩法；新图案通过正常说明页暂停学习。工具耗时和重复消耗单独记账 | 已验证；普通 UI 操作层 | 2026-10-20，GM-EV01 |
| GM-P04 | 身份、活动、运行 UI 程序集与本轮授权匹配；换身份、Play 结束、重载及超时注销回调 | 已验证的具体保护见 GM-EV03；其他分支不能由编译通过推断 | 2026-10-20，GM-EV01、GM-EV03 |

## 操作入口与已学习细节

以下从原 `learned-runtime-flows.md` 黄金矿工章节迁入。除明确标记的待验证/已失效项外，入口与观察为 **已验证（2026-10-20，GM-EV01/GM-EV02，历史 UI 事件层）**。表中 entryId 和下方分组 ID 用于后续定点更新；每条只在其记录的版本和条件下成立。所有“本轮”均指该历史体验轮次。

学习依据：FunctionPreview/.tmp/gold-miner-experience-20261020 的回执与截图；运行时重新绑定本轮身份与版本。以下只证明普通 UI 事件层，不证明触屏命中区域。

| entryId | 流程 | 已验证入口 | 完成条件和注意点 |
|---|---|---|---|
| GM-F01 | 结算后下一关 | Result.OnExitClicked → 等关闭 → LGoldMinerMgr.EnterActivity → 等主页 → OnClickChallenge | 新 CurrentSession 和 EnterLevelAck；旧 BattleView.Session 可能残留。退出结算不保证自动回到活动主页。 |
| GM-F02 | 重试 | GoldMinerResultPanel.OnRetryClicked | 新 EnterLevelAck、体力变化；这是重试同关。 |
| GM-F03 | 里程碑领奖 | GoldMinerIncomeRewardBar.OnClickNode(Claimable 节点) | claimedCfgIDs、资产、UIGetRewardList；可能一次领多档。 |
| GM-F04 | 升级 | TalentPanel.OnClickNode(groupId) → OnClickConfirm | ActvGoldMinerTalentUpgradeAck、TalentLevels、齿轮差值；先确认当前选中项和花费，界面未就绪不能继续确认。结算页进入升级后，关闭升级页不保证结算页仍在；读取实际页面，缺少结算页则正常 EnterActivity，再用主页起步阶段 phase=1，不能继续等待旧结算。 |
| GM-F05 | 补给 | OnClickGift → 当前 GiftDetailUI 的 OnFreeClickBuy/OnClickBuy | 当前商品与价格、正常到账；未知结果不重发，模拟购买不代表真实支付验证。 |
| GM-F06 | 元素说明 | BattleView.OnInfoClicked → GoldMinerRulePanel.Close | 正常生命周期负责暂停/恢复，不直接改时间或暂停字段。 |
| GM-F07 | 活动/许可页签 | 当前可见标题文本 → GetComponentInParent<TFW.UI.TFWTab> → ExecuteEvents.pointerClickHandler | 等待对应页面加载，不能把底层仍active的旧文本当作当前顶层页面。任务“领取”使用标题所在父Button上的TFW.EventTriggerListener，同样走普通pointerClick事件；它不是UnityEngine.UI.Button。 |
| GM-F08 | 首见元素教学 | GoldMinerFirstShowPanel → 看图与文案 → Close | 未读的新元素先交回视觉检查；关闭回调推进教学队列并正常恢复。第 9 关穿山甲教学实测使关卡时间停在 3559 ms，自动输入等待，没有穿透弹窗。 |
| GM-F09 | 特殊设备三选一 | TalentPanel.OnClickSlot(exclusiveGroupId) → ChoosePanel.OnClickOption(talentGroupId) → OnClickConfirm → UIMsgBox.OnClickBtn2(null,null) | 参数是互斥组 ID，不是序号。先比较实际候选描述；二次确认文字必须对应所选设备，再确认。以 ActvGoldMinerTalentUpgradeAck、TalentLevels 和资产核对选定结果。UIMsgBox 的按钮 2 只有在已核实该具体确认框时才能复用，不能当作通用“确认全部”。 |

### GM-D01：API 类型与文本读取

文本与状态读取注意：当前金币/天赋等部分文本是 `UnityEngine.UI.Text`（含 TFWText），礼包现价为 `TMPro.TMP_Text`，旧划线价格可能位于另一文本组件；不能只凭一组文本推断现价。`GoldMinerRuntimeSession.IsIncomeReached()` 是无参只读方法；`IncomeToPass()` 返回剩余差额，不是目标值。最终仍以实际页面和正常回包相互核对。

`UI.GoldMinerRulePanel` 等 Popup 是普通 C# 对象，用 `PopupManager.FindPopup<T>()` 取得；不能传给 `Object.FindObjectOfType<T>()`。规则页的可读组件是 `Game.GoldMiner.GoldMinerRuleView`。这类对象类型与 UI 文本组件必须一并缓存，避免复用时又猜类型导致编译失败。

### GM-D02：图案、教学与礼包发现

新图案识别使用实际学过的完整贴图标识集合；不能因新名字包含 `gold` 或 `stone` 就当作已学过。L17 的 `stone_breaker` 是清除周围石头的道具，不是普通石块。改成完整标识后，L18 `golden_claw` 在 93 ms 触发正常说明页暂停。

已查看的首见教学：`pangolin`（特别重的动物，喜欢在土层下穿梭）、`gem_beetle`（具有很高价值的虫子，喜欢在泥土下穿梭，很难被抓到）、`dynamite`（触碰到后会把周围的物品都炸干净）、`power_potion`（在10秒内增加拉回速度100%）、`clock`（拉回后增加关卡时间，本轮实际增加15秒）、`magnet`（触碰后吸附周围黄金）、`freeze_canister`（拉回后冻结土中移动物品10秒）、`stone_breaker`（触碰后清除周围石头）、`golden_claw`（拉回后给爪子镀金，后续物品收入提高30%）。同版客户端重复遇到时，先比较标题、说明与已学记录；一致则可直接复用正常关闭步骤，不重复分析相同截图。未匹配或视觉表现本身是测试目标时仍需看图。当前英文标题/原始键显示是已观察现象，不应被自动化误认为规范中文文案。

补充已查看教学：`slot_machine`（拉回后根据当前收入随机获得加成）。礼包轮播须检查当前箭头和下一档，不能把限购的中间档当作最后一档；本轮从 109444204 的正常右箭头继续发现了 109444205。

### GM-D03：截图完成与工具耗时

截图请求成功不等于图片已生成。`ScreenCapture.CaptureScreenshot` 是异步请求，关闭/立即重开暂停页可能没有可用新帧；L18 曾出现文件未生成及捕获黑图。实际通过正常关闭规则页、等待渲染、请求截图并等文件落地后再打开说明页恢复；已取得有效场景图。这段额外约 3.8 秒游戏时间单列为工具准备损耗，不能悄悄算成玩家操作耗时。已学习流程正常运行仍不需要每步截图。

### GM-D04：异步道具防重复

异步道具输入也必须防重复：L35 的旧辅助在50ms内请求两次时钟，因为第一条请求的延时尚未反映到当前会话。L37起缓存请求前时长、设置待确认状态，观察到时长增加后才解锁下一次，并加游戏时间间隔。结果未知时保持等待；此保护不能只以固定短暂等待代替。原始额外消耗保留在体验流水，不伪装成玩家必需成本。

### GM-D05：普通关与挑战关判据

本版正式配置的1–50关为普通关，第51关为挑战关。L51结算win=true、收入6130、奖励矿工币51，但MaxPassLevel仍为50。普通关导航模板限定stopAt≤50；挑战结算必须核对SettleAck和实际“挑战奖励”界面，不能用MaxPassLevel未递增判失败。本轮旧导航在L51写入的loss是工具误分类，原日志保留，业务结果按回包更正；不能自动进入无止境的重复挑战。

### GM-D06：模板、版本保护与实测范围

可执行导航模板：[gold-miner-advance.cs.txt](scripts/gold-miner-advance.cs.txt)。参数填到本轮 .tmp 后经 Unity execute_code 加载一次，运行中只回读摘要。模板仅处理通关后的正常导航；失败、体力不足即停，不购买、不升级、不 GM、不瞄准。输入辅助独立绑定，并填写其 `__INPUT_READY_KEY__`；每次挑战前检查辅助仍在，避免输入到期后自动开局空耗。

两个模板均绑定 `__CLIENT_MODULE_ID__`（运行 UI 程序集的 ModuleVersionId）。版本不符在替换现有回调之前拒绝安装；本轮使用不匹配的期望 ID 验证过拒绝行为，旧辅助保持注册。实际模块未修改。正确版本已经通过正常安装；正式配置版本仍须另行核对，不能把程序集 ID 当作配置哈希。

本轮已记录 7→8、8→9、9→10 三次正常衔接，退出结算到发出挑战请求约 3.00、3.00、3.54 秒，随后均收到新关卡 EnterLevelAck；L8 输入在游戏时间 50 ms 就绪。L10 失败后自动停止。原始回执和核对结果保存在 `.tmp/gold-miner-experience-20261020/learned-flow-validation.json`。这证明具体导航流程已实际复用，不代表整体速度提升倍数或其他入口已自动化。

另存 [可见画面输入模板](scripts/gold-miner-visible-input.cs.txt)，避免每轮重新实现同一套读取和操作。该模板是辅助策略，不能当作真人命中率或最优解：只按实际渲染图案、位置与当前钩角调用普通发射/道具事件，不读取隐藏目标或修改命中/收入/时间；遇到未知图案汇总后打开正常说明页等待学习。启动前填入本轮身份、活动、目录、道具使用上限与保留库存；这些参数必须来自本轮许可和资产基线。模式保持 600 秒有界，导航使用相同 `__INPUT_READY_KEY__`。重新安装只在局外或正常暂停时进行，避免重置局内策略计数。此版本的批量未知检查已整理为模板；各新增保护按当轮实际触发记录，不能只凭编译成功声称全部验证。

迁移核对：GM-EV03 的错误版本拒绝证据具体针对输入模板，不能推广为两个模板的全部保护均已实测。GM-F04 中主页 `phase=1` 是历史执行副本的调整方式；现存导航模板没有该占位参数，实际起始状态按脚本档案处理。

### GM-D07：开局与同局恢复计数

`EnterLevelAck` 不能直接按条数统计尝试；`isResume=true`、同关、未结算且体力未再扣除时并入原尝试，单列恢复过程。本轮 L21 抓取返回262016后客户端自动恢复，原始请求、回包和截图独立保存，不据此认定双钩或自动导航是根因。

### GM-D08：正常暂停学习新元素

有倒计时的玩法可在检测到未学习的可见元素时，经正常说明入口暂停并提示模型查看；禁止直接改计时或暂停字段。本轮 L12 出现未学习的 dynamite 图案，辅助在游戏时间 15 ms 打开正常规则页并保持等待，回读确认倒计时未继续；此类条件触发流程应一并保存，不能只缓存成功路径。

## 历史问题、易漏场景与复验重点

| entryId | 现象 / 结论边界 | 状态及下次动作 | 日期 / 来源 |
|---|---|---|---|
| GM-R01 | R13 原图未对齐时曾将双钩场景的 262016 直接关联原反馈；没有同关同目标的单钩/双钩对照 | 待验证：重读原图及预期图，与本次场景建立对应；不能说 R13 已修复，也不能认定双钩是根因 | 2026-10-19，GM-EV06 |
| GM-R02 | L21/L34/L47/L51 发生 262016 同局恢复；`EnterLevelAck` 数量可能大于真实开局数 | 已验证（现象）；按 isResume、关卡、结算与体力判断是否同一尝试，根因待验证；262016 与 262017 分开 | 2026-10-20，GM-EV06、GM-EV07 |
| GM-R03 | `NetMessageRecorder.MsgId` 是类型号，不是 Req/Ack 唯一流水号；部分 observer 片段有缺口 | 已验证（限制）；缺唯一关联时保留 incomplete，不能拼成完整抓取证据 | 2026-10-19/20，GM-EV01、GM-EV06 |
| GM-R04 | 原图/图片列读取为空不能证明没有图片；历史 `write-image` 曾替换旧图；后续通过图片编辑面板追加并含图导出核对 | 已验证（当时工具行为）；当前工具重新核对追加语义。表格结构及验收规范见 [运行验收 §4.2](../../references/runtime-acceptance.md#42-反馈表字段整理与格式保留) | 2026-10-19，GM-EV06 |
| GM-R05 | 历史导航把 L51 挑战胜利误判为 loss，因为 MaxPassLevel 不再增长 | 已失效：普通关进度判据不适用于挑战；采用 GM-D05 的 SettleAck 与实际挑战奖励页 | 2026-10-20，GM-EV01、GM-EV02 |
| GM-R06 | L35 旧辅助在约 50ms 内连发时钟；L37 起等时长增长，L42 约 15 秒间隔、L43 单次有实测观察 | 已失效：旧短等待重发方式。复用 GM-D04 的待确认保护并核对当前回包/资产；未触发的分支仍需验证 | 2026-10-20，GM-EV01、GM-EV06 |
| GM-R07 | 历史对齐记录包含首通奖励空配置、资产回收、购买体力上限、异常生成状态保全等未闭环问题 | 待验证：从 GM-EV05 读取决定与原要求，在本轮最终版本逐项核对；不沿用历史“待修复”作为新版本缺陷结论 | 2026-10-14，GM-EV05 |

## 可复用运行脚本

完整参数、哈希、宿主、操作影响、起始状态及注销方式见 [脚本档案](scripts/usage.md)。两份原模板保留唯一源路径，本次整理没有改动脚本字节。

| scriptId | 模板 | 实际验证范围 |
|---|---|---|
| GM-S01 | [普通关导航](scripts/gold-miner-advance.cs.txt) | 历史普通关衔接、输入就绪与失败停止；当前文件的全部保护未逐项重跑 |
| GM-S02 | [可见画面输入](scripts/gold-miner-visible-input.cs.txt) | 历史正常事件输入、首见图案暂停及版本不符拒绝；辅助策略不代表真人命中率或最优解 |

## 更新记录

| 日期 | 变更 | 验证与剩余条件 |
|---|---|---|
| 2026-10-21 | 从已学习流程迁入黄金矿工详情；补充来源、版本、定位、环境、问题状态、稳定条目 ID；登记 GM-S01/GM-S02 | 整理和文件核验，不是重新运行验收。保留原运行证据、原脚本及待验证问题；未来每阶段自动增量更新 |
| 2026-10-21 | 按功能集中到 `features/k1-gold-miner/`，经验与 `scripts/` 一起维护，统一索引留在 `features/index.md` | 目录与引用调整；脚本内容和历史验证范围不变 |

## 活动结束防漏检查

- 活动结束按 [生命周期合同](../../references/activity-lifecycle.md) 单独核对排行邮件、已达未领奖励补发、外围奖励、六类活动资产回收、临时进度清理和未完成局终止；单局结算或正常通关不能代替这些断言。
- 补验缺口保留稳定 ID、独立断言及关闭证据；仅检测活动离开进行状态，不证明邮件、附件、到账或跨期清理完成。
