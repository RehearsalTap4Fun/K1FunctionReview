# 次元商店与兑换商店验收经验

featureId：k1-commerce-shops。关联 NK-10651、NK-10644，2026-10-29 Unity 版本日补验。历史结果不能替代本轮验证。

## 再次验收先看

区分已加载资源、真实业务扣奖、普通页面旅程和多语言显示。次元商店从合并商店正常入口进入，兑换商店还受整服开放周期约束；先核当前实际规则，不复用旧日期。头像框兑换发的是待使用券，hasOwn=false 与券仍在包中并不矛盾。

## documentBaseline

- status：needs_review。
- source：https://jira.tap4fun.com/browse/NK-10651 、https://jira.tap4fun.com/browse/NK-10644 ；本次已读取资料保存在下述私有 S1 批次。
- confirmedVersion / confirmedAt：无完整静态对齐确认，不补造。
- currentVersion / checkedAt：2026-10-29 本轮 plan-new-environment.json 文档基线；未把版本表时间当需求版本。
- nextAction：复用前核本轮原需求及版本差异；本档案仅保存运行方法和历史现象。

## 来源

S1：FunctionPreview/.tmp/k1-599-supplement-20261029/commerce-runtime/，2026-10-29；client 529503dad1638e8b5d159c2ce6fd9d1b8bef1d8c、server 242b2db3eb2a3d206a17e491da7ed4283dbce235、config f904ffa7a7a9dc55f5173e71b7a3ed3216ffd263、生成客户端 f19a56c9d7dda8b1a4ba726d024e5b0512a24168。原图、身份、回执不随 Skill 分发。

S600-UI：2026-11-03，仅通用 Unity 截帧与文件留存方法复核，不是商店业务复验。客户端正式转换产物 bc585159f5c2b00e8b50f4d029da5fb97fd61f51；私有索引 `FunctionPreview/.tmp/k1-600-unity-20261103/king-entry-followup/en-ru-review-20261103/image-review.json`、`arena-ui-language-review/visual-review.json`、`arena-ui-language-review/root-handoff-facts.json`。后两路径同属该批次根目录；接收者缺本地材料时来源不可访问，先复核。截图、原始回执和身份不随 Skill 分发。

## 已验证操作方法

下列条目默认属于 2026-10-29 / S1；另标日期/来源者按其范围读取。具体账号、实例、费用和授权每轮重核。

| entryId | 方法与完成信号 | 边界及下次动作 |
|---|---|---|
| commerce-loaded-bytes | 实读 IsUseBytesConfig 与新增商品关键值，再对正常页面 | 磁盘导入不等于运行时已加载 |
| commerce-real-click | 控件可能同时挂空 Button 和实际 EventTriggerListener.onClick，按真实注册监听执行 | 空 Button 调用无效是驱动问题，先核监听再判断产品 |
| commerce-tab-click | TFWTab 正常 OnPointerClick 才触发切页业务 | 仅设 isOn 不证明实际页已切换 |
| commerce-top-popup | 框兑换后自动 UsePrompt 要先正常处理，再继续下一页 | 覆盖层下调用底层控件不算完整玩家旅程 |
| commerce-frame-voucher | 正常兑换扣款、券增量、已拥有排序、重登持久化分别核验 | 未使用券不等于奖励丢失；已拥有分支不再弹兑换确认 |
| commerce-language-flow | 设置页语言 Toggle 与行 Click→正常确认→重启→核同一实际角色和语言 | 不直接伪造语言缓存 |
| commerce-screenshot-frame | CaptureScreenshot 只请求帧尾采图；同一调用后立即导航、关闭或重开会截到后继页面。将导航、等待稳定帧、截图落盘、实际看图分开；核对图中真实面板，不只读 text | 辅助 capture 可能以同 basename 重写 JSON，业务/协议 dump 固定另存 `*-data.json`，稳定图片另命名；旧 dump 被覆盖后不能把 texts 回读冒充原始绑定数据。共享文件被后续批次刷新时冻结副本并重新看图/校验哈希。已验证取证陷阱，2026-11-03/S600-UI；不代表商店本轮重测 |
| commerce-glyph-boundary | 看实际原图并投影实际字形顶点核裁切；英语可与阿语、俄语结果不同 | RectTransform 越屏本身不足以证明字形裁切 |
| commerce-esc-focus | 原生 Escape 未进入 Input、Application.isFocused=false 且键盘采样为空时记输入能力阻塞 | SendEvent/SimulateKeyBack 不代替真实键盘；不可凭弹窗未关判产品失败 |
| commerce-online-images | 当前 DOM 图片缩略可能是 div[src]；读取实际 DOM 后普通 locator.click 可打开在线预览 | 不猜旧 tab.cua 能力；表全局图片索引不等于单格数量；追加后逐图打开确认保留 |

## 本批业务观察

次元商品119正常单次兑换及三语显示通过；兑换框105正常扣款、发券与重登持久化通过。早期两项均缺本批实际 ESC 输入证据。2026-10-29 20:38（北京时间）已补齐次元商店真实ESC及重进，次元商店本项闭环；兑换商店由原表人工保持完成，本次未重开，其独立UI/ESC历史证据边界不改写。

S2：同一私有批次 `case47-native-esc-verified-results.json`、`arena-root/eligible47-native-esc-*-data.json` 及原尺寸截图。

| entryId | 方法与完成信号 | 边界及下次动作 |
|---|---|---|
| commerce-esc-native-recovered | 实际Unity窗口GameView空白区原生点击后核appFocused=true；Sky原生Escape关闭次元整店且CITY HUD保持。正常重进、普通119详情后Escape仅关详情，再Escape关整店；购买量119前后均1，没有再购买。 | 仅ESC缺口补验，原入口/点击/状态采集仍走Unity MCP；不因EditorWindow.Focus或发送键盘工具成功就声称收到输入。下一轮仍先核实际焦点。已验证2026-10-29/S2。 |

兑换商店有两项独立界面问题：底部说明在阿语约3px、俄语约17px被裁，计同一问题；俄语框108长标题与关闭按钮重叠约22px为另一问题。英语对应页面未复现。原始依据见 S1 的 receipt48-ui-ar-final.json、receipt48-ui-ru.json 及对应原图。再次验收重看实际修订画面，不将历史缺陷直接判为当前失败。

## 脚本与留存

暂无脱离本轮身份绑定并逐字验证的通用业务脚本，执行副本保留 S1。原始证据仍被本轮台账及补验依赖，未删除。2026-10-29 新增本档案并登记索引。

2026-11-03：仅增量修订 `commerce-screenshot-frame`，合并 S600-UI 的错帧、同名 dump 覆盖及稳定副本教训；其他历史业务结果与文档确认标记保持原范围。未新增脚本。

## 2026-11-04 / 600-29 每日特购增量

本节复用稳定 featureId `k1-commerce-shops` 登记商城内每日特购，不另建同类商城档案。关联 NK-10647「礼包 - 数值 - 每日定制内容优化」，实际功能为 Type26 / GiftTypeEnum.DailyDeal / UI.DailyDealPage；GiftTypeEnum.DailyMadeGift=44 是另一功能。上文次元/兑换商店的需求标记、历史业务与ESC结果均保留原范围，不能移用为每日特购的结论。

最近实际验证：2026-11-04，mainline_regression，仅Unity；600-29发布 **5通过、2阻塞**，fullyAccepted=false、titleScopedAccepted=false。当前118102分支显示与一次真实Test结算已有证据；真实ESC和另一118101分支未验证。原生SDK付款、重复订单/限购拒绝不在本次通过范围。

### 每日特购 documentBaseline

| 字段 | 内容 |
|---|---|
| status | needs_review |
| source | [NK-10647](https://jira.tap4fun.com/browse/NK-10647)；标题「礼包 - 数值 - 每日定制内容优化」；**正文非空：“数值调整：所有礼包的性价比调整”** |
| confirmedVersion / confirmedAt / precheckRunId | 无具体目标数值或关联开发文档的确认与回读依据，不补造 |
| currentVersion / checkedAt | a0019ef40706970c010f77802c32e7187c8cacd3bf74d49f5b0ab9e07bb02f19 / 2026-11-04T13:37:14.815209+08:00 |
| evidence | S600-D29 的runtime/600-29/source.json及已发布plan.documentBaseline |
| reason / nextAction | 正文泛称性价比调整，没有目标数值；只能核正式源一致与当前玩家体验。此基线没有basisType=jira_title，不把正文非空误归类成标题级基线；补齐目标后只对齐受影响规则 |

### 每日特购来源与实际版本

S600-D29：`FunctionPreview/.tmp/k1-600-round-20261103-2128/`，2026-11-04。本地原始证据、账号、测试订单、反馈表身份和绑定脚本不随Skill分发；来源在接收者机器不可访问时，当前可复用性待复核。整理经验不代表重新执行业务。

| 来源ID | 定位 | 验证层级 / 边界 |
|---|---|---|
| S600-D29-published | runtime/600-29/published-20261104-1350/runtime-result.json、summary.html | 已发布5通过2阻塞；Client实际07e959519e793439ba4416fa7c794c554bf5bd25+获批本地无效using删除，源码基线90abb924cd5a32ed20b1de5e5d7a5cfbdaa2dd3c；Server1deeaf9332bf677094853e9c2a798c3bb8acb20f；Configebdfe05f07745d86184fe5a6f7af3c3dd0cdf178；正式转换1322 |
| S600-D29-readback | 600-29-result-readback-20261104-134956.json | 实际版本行回读已记录5通过及2条待补，未宣称正常SDK付款或完整性价比目标通过；私有文档身份留本轮 |
| S600-D29-source | config-evidence/workbook-reads.json、root-and-reward-reads.json、2914-runtime-handoff.md；bridge/group10-new-role-effective-preflight-1.json | 正式Group10/custom10源与实际载入；正式XLSX为源，运行对象验证生效，未手改生成配置 |
| S600-D29-ui | bridge/dailydeal-open-unlocked-state-1.json、dailydeal-normal-scroll-right-1.json、dailydeal-actual-new-reward-detail-click-1.json；ui/active-cn-20261104-054348-740.png、active-cn-20261104-054643-954.png、active-cn-20261104-054424-196.png | 实际DailyDealPage奖励格、正常滚动首末、1100147详情；原图由主协调本轮查看 |
| S600-D29-order | bridge/dailydeal-test-order-outcome-2.json、dailydeal-after-reentry-assets-1.json；runtime/600-29/test-order-server-log.json；ui/active-cn-20261104-054700-951.png、active-cn-20261104-054823-860.png | 本人真实服务器Channel Test单次结算/买次/库存/重进，非正常按钮SDK支付；具体订单只在本轮私有回执 |
| S600-D29-close | runtime/600-29/native-interruption.json；bridge/dailydeal-after-close-popups-1.json、dailydeal-purchased-reentry-state-1.json、dailydeal-final-popups-1.json、dailydeal-final-observers-cleanup-1.json | 物理ESC停止Computer Use，未向Unity发ESC；仅MCP生命周期关闭和正常入口重进、清理注销有证据 |

### 每日特购可复用方法与前置

以下条目实际验证日期均2026-11-04，适用Client/Config同S600-D29；历史账号、SID和GM许可不构成后续授权。版本变化先核正式源、页面配置和实际接口。

| entryId | 方法 / 成功信号 | 状态、边界与下一次动作 | 来源 |
|---|---|---|---|
| commerce-dailydeal-type | GiftTypeEnum.DailyDeal=26；GameData.I.GiftData.GetPeriodGiftData(giftId,GiftTypeEnum.DailyDeal)；DailyDealMgr.IsDataReady；实际DailyDealPage的_gift/GetReward | 已验证。118101/118102不是DailyMadeGift44；源表候选存在不等于服务器本周期有效 | S600-D29-source,ui |
| commerce-dailydeal-shop-tab | `ShopJumpMark.GetByTabConfig(10069)` → `Logic.ShopMgr.I.OpenShopPanel(mark)`，等实际DailyDealPage打开再截图/读状态 | 已验证当前页面移入shop入口。旧`ShopJumpMark.dailyDeal`模板只查special，在本版本不适配；后续先读实际TabConfig入口，不把方法return当页面已开 | S600-D29-ui；bridge/dailydeal-shop-tab-open-unlocked-1.json |
| commerce-dailydeal-old-special-mark | 旧dailyDeal mark可定位每日特购的建议 | 已失效，仅当前10069位于shop的配置范围；被commerce-dailydeal-shop-tab替代，不据此推断老版本入口也失效 | S600-D29-published |
| commerce-dailydeal-min-stage | 先自然完成101；本人角色门槛未满足时，按当轮许可使用已注册`setroguelvl 5`准备可挑战5/已通4，再读权威回包与CurrGameLevel | 已验证仅最低解锁前置，保留角色进度/星级/排行及相关缓存副作用，不代表实战通关2–4。该批返回CurrGameLevel=4、ADshopOpen=4；下轮阈值重新读，不盲复用5 | bridge/dailydeal-minimum-own-stage-fixture-1.json、dailydeal-minimum-own-stage-outcome-2.json、S600-D29-published |
| commerce-dailydeal-vr1 | 当前真实118102有效且买次0，正式Reward=[118104]；实际VersionRewardMgr.currentVersion=1，逐typ/id/val比对Gift.GetReward和基础View | 已验证VR1当前分支；118101→118103仅正式源/运行配置映射核对，不算118101玩家旅程已验；不外推其它23版本档运行通过 | S600-D29-source,ui |
| commerce-dailydeal-eight-cells | 实际9项View抽出30020001充值点后，8格+500充值点标签；正常水平滚动看首末全部格；真实1100147点击弹橙色通用英雄卡详情 | 已验证图标/名称/数量与正常滚动。当前118104含1100147×1，不含旧3000034；八格、六普通库存物品、500钻和VIP/充值点是不同口径，不能仅按格数判少奖 | S600-D29-ui |
| commerce-dailydeal-test-settlement | 先存本人当前有效未购gift/资产/买次并注册只读观察器，唯一订单仅一次`buyGiftTest`；核服务器Channel Test、UpdateGiftNtf Bought1、GiftRewardNtf与实际增量 | 已验证服务器测试通道结算：3320034/3320023/3320024/3320046/3320041/1100147分别+5/+10/+1/+80/+115/+1，钻石35→535；旧3000034不增。不是按钮购买/SDK付款、限购拒绝、重复订单幂等或零副作用证明；未知结果先回读不重放 | S600-D29-order |
| commerce-dailydeal-reentry-no-extra | 正常确认奖励窗、MCP关闭商城，从相同10069产品入口重新进入，买次仍1，库存/钻石无额外增量 | 已验证正常关闭重进不重复发奖；不等于重复支付请求防重，不等于ESC返回 | S600-D29-order,close |
| commerce-dailydeal-esc-blocked | 原生接入准备时用户物理ESC停止Computer Use，取窗口前即停止，未发任何Unity ESC | 待验证。该批不再调用CU；MCP Close不能补成真实ESC。以后得到可用原生输入范围后，在实际详情/商城分别补ESC前后图、HUD与重进 | S600-D29-close |
| commerce-dailydeal-opposite-filter | 118101条件is_cross!=1，118102为is_cross==1，且需要实际Group10有效角色/周期 | 待验证。本轮只有真实118102；118101缺数据，不反射注入GiftInfo、不改Filters。另一既有角色使用Group9，不能代替custom10的118103旅程；需另有明确分配且满足相反过滤条件的本人Group10角色 | S600-D29-source,published |

### 结果边界、适配与留存

本次替换物品未改文案/布局，按当前中文1080×1920定向观察实际道具名、图标、数量和可滚区域；无新增三语/尺寸专项通过结论。1100147详情是原有组件真实显示，不能仅因打开详情扩大语言范围。完整“所有礼包性价比”目标仍缺具体数值依据，documentBaseline保持needs_review。

一次Channel Test交易仍有真实测试角色副作用：上述六道具和500钻、10VIP与500充值点、买次1，以及个人付费/每日累计/首充等记录保留，并同步本人跨服缓存。没有真实扣费、没有清付款/背包、没有重放订单；不把测试通道解释为完全无副作用。最低已通4/可挑战5前置和正常101完成继续保留，没有回滚进度或改服时间。

已正常确认奖励窗、关闭商城，最后弹层栈空；GM/购买观察器已注销，语言保持cn。Computer Use在用户物理ESC停止后本轮未再调用原生输入；**真实ESC仍阻塞**，不挪用本档案其它商店或600-27的ESC通过结论。原始证据为发布/补验依赖，未删除。

无新增共享脚本：身份绑定dailydeal*执行副本和具体订单仅保留本轮目录；未复制到Skill，不新建scripts空目录。后续先复读本节入口/过滤/付款边界，按新身份、商品价格、实例与资源授权生成受控副本，未知支付结果只回读。

更新记录：2026-11-04追加commerce-dailydeal-*十条稳定经验及独立NK-10647文档标记；保存5通过2阻塞、正常入口修正、一次Test真实结算和两项缺口。此前所有次元/兑换/通用UI条目原文保留；未提交或推送。


## 2026-11-04 15:25 每日特购服级过滤更正

commerce-dailydeal-cross-server-level：冻结is_cross函数虽然接受p却完全不读取玩家；common.InCrossCycle→gdconf.InCrossActvProgress按服务器开服时间、周期与当前服时间判断。因此当前2914从新本人角色切回SDK已证归属的旧本人角色，不能改变118102/118104为118101/118103，未做无效切号。反向分支真正需要已分配、处于非cross周期的Group10服环境，不得改时钟、开服数据或filter造态。

本次仅补来源核查，无新Unity/付款/奖励动作；原5通过2阻塞保持，运行时间沿原记录，真实ESC仍未测。Jira正文的完整性价比目标仍needs_review。新报告见FunctionPreview/.tmp/k1-600-round-20261103-2128/runtime/600-29/published-filter-correction-20261104-152509；在线待验收回读600-29-result-readback-20261104-152516.json；精确调用链ui-cases/d29-cross-filter-readonly.json。
