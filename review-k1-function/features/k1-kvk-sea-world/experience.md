# KVK 海底世界：运行环境与验收经验

| 字段 | 内容 |
|---|---|
| featureId | k1-kvk-sea-world |
| 关联需求 | NK-10712、NK-10714、NK-10707、NK-10715、NK-10735；NK-10886、NK-10887、NK-10888；NK-10924、NK-10993 |
| 更新时间 / 实际验证 | 2026-11-18 Asia/Shanghai（602 NK-10993 阻塞记录）；2026-11-12 601版本日Unity（NK-10924）；2026-11-04维护（600 Unity有限范围，见KVK-600-E1）；2026-10-29 599版本日Unity |
| 版本 | 599：客户端529503da/服务器242b2db3/配置f904ffa7；600：实际客户端07e95951/服务器1deeaf93/配置ebdfe05f，规划90abb924在KVK目录与LSeason的差分为空 |

## 再次验收先看

下述是环境验证经验，**对应业务尚未通过**。历史服务器、账号和许可不能复用为新轮授权。

## documentBaseline

status=needs_review；本档案没有独立功能PRD确认标记。原599行和本轮冻结玩家旅程仅作为任务来源，下轮读取实际PRD与原问题再对齐，不能从本环境经验推定完整需求已确认。

600补充：status仍needs_review；source为NK-10886/NK-10887/NK-10888标题、重复正文及自动提交评论，无独立PRD确认。currentVersion=7f60dddf8711484e031447f0c24cec528ee126891d0f327d6bfa8a700896cd97；checkedAt=2026-11-04T14:24:37.630731+08:00。未补confirmedVersion/confirmedAt，不将标题来源或实现契约当预检后文档确认；赛季口径、动态刷新及完整生命周期规则仍待明确。

## 方法、限制和留存

来源 KVK-599-E1：`FunctionPreview/.tmp/k1-599-supplement-20261029/` 下 `backend/private-kvk-authoritative-scene.json`、`kvk-live-context-source/`、`arena-root/eligible01-cn-owned-throne-data.json`、`backend/private-kvk-shared-match-absent-after.json`；实际ID/角色/回执只保留原批次，不随Skill分享。

| entryId | 结论 / 下次动作 | 状态 |
|---|---|---|
| KVK-STANDALONE-SCENE | 现有kvk_setup_test、真实SetMatchResult及kvk_c能在本人独立battle生成持久化真实地图。MapType10032/nav9/npcRefresh5/tag4；“Map5”不能误写成实际MapType ID。以真实battle_scene、正常实体广播、渲染实体和普通地图点击核验，不以exec succ判成功。 | 已验证：仅独立地图夹具 |
| KVK-TEMPLATE-BOUNDARY | 独立地图ActvID=0不产生真实85活动的KvkUnionTmplInfoNtf。实际跨服场景成立而LPlayer.kvkTag仍0，会走旧详情，可能看到默认捐献/攻击按钮。缺有效模板时不能据此判真实海世界路径失败，也不能手写kvkTag或注入Ntf凑通过。先取得完整隔离的85活动/报名链。 | 已验证：上下文缺口；业务待验证 |
| KVK-SHARED-MATCH | 599共享match版本92c8e7e3属历史，当轮未执行openkvk、全局Match配置变更或RecordTag写入；600只读复核两个人服实际共用GlobalMQ及同一global.match.all订阅，当前Match运行镜像未核，不沿用旧版本。真实85阶段同步仍会改匹配阶段/历史，新空tag也有影响；独立game/battle不足以证明Match隔离。来源KVK-599-E1、KVK-600-E1，下次先核实际路由/存储与全部实例分配，不复用历史授权。 | 已核冻结源码及600实际共享路由；完整隔离/业务待验 |
| KVK-THRONE-FIXTURE | 注册kvkfort setowner可准备真实归属，冻结版本不发首占奖、不收赛季；仍会清争夺/驻军并更新领土、属性、任务与纪事。只能对已核实全自控场景操作。kvk_reduce会动全部未开放建筑，若还有早领窗口，应避免全量操作；本批仅对单个王座解锁截止准备，正常tick开放。GM归属不等于个人真实驻守时长。 | 已验证：前置副作用；正常占领/时长未通过 |
| KVK-ENTRY-CLEANUP | kvk_gm_enter_scene异步后，GS City字段可仍本服；真实battle日志、跨服客户端与实体需联合判断。配对leave后本批客户端已回本服/CITY且inWar=false、CN、观察器卸载；私有地图日志仍保留1个City/MapPlayer记录，不能宣称地图数据已删除。保留场景并披露，勿为清理擅自强End/删库。 | 已验证：客户端恢复；服务器夹具保留 |
| KVK-SEAWORLD-WILDHUNT-601 | 2026-11-12 NK-10924 用这条链在本人 gs+新建 battle 上取得真实海世界路径（kvkTag=4、SceneTypeKvk）：新建 battle（SID 后三位须与主机所有容器不同，端口=base+sid%1000）→ door `create_test_union <pid>` → `openkvk 100004 <pid> <battle> 5 4`（共享 match 只新增一条空匹配记录）→ `settrainlv <pid> 101`（满足进入门槛 >100）→ 客户端重登 → HUD「深海遗迹」「进入」→ `actv newActv 1093502`（荒野狩猎 KvkTag=4）→ `actv wildHuntSummon <pid>`。荒野狩猎宫格要在 KVK 场景内才能点开；宫格/页签需用射线点击（down/up/click），直接发 pointerClick 不生效。退出走海世界页「退出」→「确认返回本服」。 | 已验证：Unity 路径，单账号；「加入」路径需同盟第二账号 |
| KVK-EVILGUARD-602 | 2026-11-17 NK-10993（kvk4 恶魔守卫搜索）阻塞：新建 battle 12606 两次都起不来——dev 配置 6340e8e8 的 AvatarFrameNewCfg 103140（NK-10779）缺 NK-10778 新增必填 LevelGroup → 服务端加载 FATAL（Jenkins #12384）；改用旧配置分支又缺 AvatarFrameLevelCfg（#12385）。续验路线：配置修好后重建 battle（dev/dev）→ `openkvk 100004 <pid> <battle> 5 4` → 重登 → 深海遗迹 → 搜索恶魔守卫。代码入口：服务端 `ctl_map.go` SearchRefreshEvilBossMultiLv、`map_kvk_boss_evil.go` GetKvkEvilGuardClearance；客户端 `UISearch.cs`（Mass/Btn2 恶魔、KVK4 等级滑条）；D2Search 13001 → NpcClassID 41000017。 | 阻塞：环境；业务未验 |

没有可直接运行的通用造场脚本；本批辅助脚本含绑定身份，不分享为默认执行入口。三语、ESC、真正85生命周期及结算仍需完整活动前置。

## 600版本日Unity增量（KVK-600-E1）

2026-11-04，NK-10886/10887/10888实际类型为任务/子任务，按mainline_regression玩家旅程组织；仅Unity，真机为用户明确范围外。12用例中入口1通过、其余11阻塞；24断言中1通过/23阻塞，其中普通成员服务端拒绝半支另有真实通过证据，未测自然按钮保留。生命周期阶段仍unknown、24补验义务open；不是完整KVK报名权限或活动通过。

来源：`FunctionPreview/.tmp/k1-600-round-20261103-2128/runtime/60026/published-20261104-142138/summary.html`、同目录runtime-result.json，以及`readonly-recovery/`和本轮bridge回执。来源为私有本地运行证据，不随Skill分发；接收者不可访问时，定位方法可参考，运行状态必须重核。实际client07e959519e793439ba4416fa7c794c554bf5bd25与规划90abb在本功能范围差分为空；server1deeaf9332bf677094853e9c2a798c3bb8acb20f、configebdfe05f07745d86184fe5a6f7af3c3dd0cdf178。

| entryId | 结论 / 下次动作 | 状态与验证范围 |
|---|---|---|
| KVK-ACTIVITY-CENTER-GATE | ShowActivityByCfgId还查ActivityCenterOpenState及活动switch；CheckActivityVisible=0或单个Visible=true不能替代整体入口门槛。冻结正式Config1045 NewUnlockActivity：root50，Group10为5；实际低一关角色被入口拒绝。下次按实际分支/当前关卡核门槛，正常推进最小前置，不误推root50或改缓存。 | 600已验证正常入口/门槛；不代表Apply报名页通过 |
| KVK-SEASON-REFERENCE | 客户端LSeason来自KvkInfoAck.SeasonID/GetServerSeasonId，GS报名gate用conf.GetVersion/RewardVer；本轮实际两者1与18并存，活动标题显示18也不能证明LSeason18。setrewardver不会同步前者且有全服副作用。下次先读两个口径，在真实Apply页验证并找产品明确口径，不能手改LSeason/kvkTag或注入Ntf。 | 已核源码与实际口径；是否违反产品规则待验证 |
| KVK-BASIC-AUTH-REJECTION | UnionCheckOp先查阶级Permission再查官职Position；普通成员仅在Class/Position都核实无authority49时才是安全拒绝样本。本人真实普通ApplyReq回9022 ErrCodeNotHasUnionAuthority，client报名与Mongo前后未变，日志命中提前return；未用NoUnion/资格错误代替。下次监听专属Ack、前后只读本人的报名/职位/联盟快照，未知结果不重发。 | 600服务端原权限半支已实测；自然Apply按钮/UI半支未测 |
| KVK-CANCEL-PHASE-GUARD | OnCancel外层无phaseguard，但最终SendKvkUnionCancel2Match在CurState>Marching返回；Btl权限通过时可能无正常Ack，不能当最后一天7739。Apply发送函数无同样guard，资格通过仍会发MQ。下次沿调用链核到真正发送点，不只看入口函数，也不盲发取消。 | 冻结1deeaf93源码已核；本轮没有执行取消 |
| KVK-LIFECYCLE-PERSISTENCE | 85正常Close保存活动及进度并保留历史；battle另有结束撤军/退出及3日后清表，不能把客户端退出当删场景。ResetPlayerKvkMgr按FinishRecord回收：水晶×7换币、珍珠floor(n/10)按Effects返钻石。排行IsReward前置与消息队列受理都不能证明邮件/资产落地；BP自动未领补发路径被注释，策略待产品明确。下次用完整隔离真实85/Match/Battle及本人邮件/资产逐副作用取证，关注失败恢复和晚到资产。 | 600精确冻结源与正式Excel已核；生命周期业务及故障恢复未实测 |
| KVK-INPUT-CLEANUP | 本轮KVK页正常自身Close、专属监听注销、临时登录flags恢复；API关闭不是ESC。用户停止本轮原生CU后没有再发原生输入，真实ESC保留工具缺口。后出现独立邀请营销popup不当作KVK半退出，也不为清理强关Popup根节点或宣称全栈空。 | 600正常收尾已核；真实ESC仍待验 |

没有归档含本轮固定账号/服务器的通用脚本；一次性绑定执行副本留本轮私有目录。经验维护不变更文档确认状态，不继承当前账号/服务器/时间或发布授权，也不关闭尚未通过的断言。
