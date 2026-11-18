# 功能验收经验索引

按名称、别名、关联需求或分支找到档案后，执行 [经验读写规则](../references/feature-experience.md)。只读取本次相关档案；更新时间是档案维护时间，不是业务重新验证时间。

| featureId | 功能 | 别名 / 搜索词 | 关联需求 / 历史分支 | 历史证据范围 | 档案 | 更新日期 |
|---|---|---|---|---|---|---|
| k1-giant-snake-phase4 | 巨蛇大作战4期 | 肉鸽塔防4期、Phase4Minion、混合无尽、计次盾 | NK-10652、NK-10657 / dev_NK-10652 | Unity首轮14通过/25失败/46阻塞，18项处理决定已确认；S-07（6c248026）第27至40关通关，满星11,956分结算被247172拒绝，校验表仅1–700，7笔Editor模拟购买与重登清理留证；S-07（96a62eb8）第41关满星12,082分/13:40，同步与结算被247172拒绝、排行只记早期同步（#61）、主动退出后需重登（#68），#63血量成长通过、#65返回提示截断；含无尽监控、bot和探针模板 | [巨蛇四期档案](k1-giant-snake-phase4/experience.md) | 2026-11-11 |
| k1-gm-auto-occupy | GM 自动占领 | LGmAutoOccupy、王座、禁迁、自动迁城 | dev_NK-9557 / 用户定向修复实测 | Unity真实迁城及107项回归通过；出兵被王战None状态拦截，待整服前置授权 | [自动占领档案](k1-gm-auto-occupy/experience.md) | 2026-11-02 |
| k1-kvk-sea-world | KVK海底世界 | 王座、KVK4、报名权限、动态赛季开关、独立地图、85模板、匹配隔离、深海遗迹、荒野狩猎 | NK-10712、NK-10714、NK-10707、NK-10715、NK-10735；NK-10886、NK-10887、NK-10888；NK-10924、NK-10993 / dev | 599独立地图和真实归属前置已验证，缺真实85模板；600真实入口及普通成员被服务端拒绝已验证，报名页/权限/三语/生命周期待补，文档needs_review；601 NK-10924搭建真实海世界，「围剿」集结弹窗无遮挡，「加入」需同盟第二账号待补；602 NK-10993恶魔守卫因dev配置FATAL导致battle未启动，阻塞未验 | [KVK海世界档案](k1-kvk-sea-world/experience.md) | 2026-11-18 |
| k1-lava-cave | 熔岩洞穴与科技扣费 | LavaCave、AP、批量科技升级 | NK-10750 / dev | Unity正常合法扣费、资源不足无副作用、单升/批升预算旅程通过 | [熔岩洞穴档案](k1-lava-cave/experience.md) | 2026-10-29 |
| k1-strongest-trial | 强者试炼 | type151、CommonScoreRank、白金兑换券、紫箱 | NK-10648 / dev | Unity真实奖励预览与1194000分入榜前态；双榜邮件自然End仍待验 | [强者试炼档案](k1-strongest-trial/experience.md) | 2026-10-29 |
| k1-commerce-shops | 次元、兑换与每日特购商城 | UIMergeShop、TFWTab、头像框券、城堡预览、稳定截图、DailyDeal、Type26、10069 | NK-10651、NK-10644、NK-10647 / dev | 次元商店最小购买、三语及真实ESC重进闭环；兑换商店历史适配问题和人工完成决定分开保留；11/03仅追加通用截帧/留存方法复核；11/04每日特购5通过2阻塞，118102/VR1与一次Test结算已核，真实ESC/非cross服周期118101待补，完整数值目标待确认 | [商业商店档案](k1-commerce-shops/experience.md) | 2026-11-04 |
| k1-arena | 竞技场 | ArenaV2、阵容快照、重复挑战、积分分档匹配、三语与多图反馈、原生拖动输入 | NK-10402 / dev_NK-10402；NK-10371、NK-10459（已发MR，599排除） | 10/27历史21项保留；10/29原32/33未合dev误纳入，技术实测仅开发参考，不计599通过/失败、不移挂其他项；11/03仅追加UI取证与输入能力方法；11/03 Unity一期中文定向复验3通过、2待补，非全需求通过（600-2904-IMPACT-20261103）；11/04仅来源/已有缓存接续0新增业务通过，36真实任务非724，ReqQuery非严格只读，人工听感仍待验 | [竞技场验收档案](k1-arena/experience.md) | 2026-11-04 |
| k1-gold-miner | 黄金矿工 | GoldMiner、Gold Miner、矿工、挖矿活动、特殊设备、矿工币、ESC、返回键、HUD | NK-8062 / dev_NK-8062 | 玩家体验、反馈与运行片段；含 MuMu 连续帧普通输入体验（4–18 关通过，含标记目标优先、每局免费炸弹、钻石补体力及规则文案歧义），返回键后 HUD 消失仍待复验，非全功能通过；10/29追加实例GM/跨服排行隔离前置只读核证 | [黄金矿工验收档案](k1-gold-miner/experience.md) | 2026-10-29 |
| k1-world-map-rework | 大地图重构 | WorldMapV2、V2Fort、FogLayer、新大地图 | NK-8604 / dev_NK-8604 | 多批次静态预检；历史阻断待复核 | [大地图重构档案](k1-world-map-rework/experience.md) | 2026-10-21 |
| k1-first-day-fog-spawn | 新服大地图出生与随机迁城首日迷雾一致性 | 首日迷雾、D0 出生区、随机迁城、FogLayer | 2026-08-11 专项请求；相关 NK-8604 / dev_NK-8604 | 静态可进入运行验收；未执行运行验证 | [出生与迷雾档案](k1-first-day-fog-spawn/experience.md) | 2026-10-21 |
| k1-alliance-bi-recommendations | 联盟 BI 推荐场景 1–5 | 联盟BI推荐、union_bi_rec、BI 干预、AI 盟主、付费邀请 | NK-8728 / dev_NK-8728 | 静态预检及配置快照；历史阻断待复核 | [联盟 BI 档案](k1-alliance-bi-recommendations/experience.md) | 2026-10-21 |
| k1-hero-bonds | 羁绊系统调整 | 英雄羁绊、HeroBondMech、羁绊战斗机制 | NK-8953 / dev_NK-8953 | 静态预检；Mock 与真实链路待复核 | [羁绊档案](k1-hero-bonds/experience.md) | 2026-10-21 |
| k1-treasure-wear | 宝藏磨损度 | KingdomTreasure、Wear、王国宝藏磨损、最低磨损记录 | NK-8946 / dev_NK-8946 | 静态预检及生成 JSON 辅助检查；未运行 | [宝藏磨损度档案](k1-treasure-wear/experience.md) | 2026-10-21 |
| k1-cold-server-recruitment | 冷库服与召集活动调整 | 冷库迁服、冷库召集、ColdServer、coldsrc、UnionCross | NK-9710 / dev_NK-9710、dev | 历史全功能矩阵保留；10/29追加真实空列表、三语与原生ESC闭环，发布详情夹具另记缺口 | [冷库服档案](k1-cold-server-recruitment/experience.md) | 2026-10-29 |
| k1-google-play-achievements | Google Play 成就接入 | Google Play 成就、CPE 成就、CpeTask、LittleGameAchievement | NK-8028 / dev_NK-8028 | 0 完整通过、8 部分、24 阻塞、8 待 Android | [Google Play 成就档案](k1-google-play-achievements/experience.md) | 2026-10-21 |
| k1-radar-monster-first-kill | 雷达怪物击杀计数优化 | 普通雷达怪、雷达规则更新、选级、攻击、首杀隔离 | NK-9973、配套 NK-9974 / dev_NK-9973 | 1 通过、3 部分、20 阻塞；真实战斗未闭环 | [雷达怪物档案](k1-radar-monster-first-kill/experience.md) | 2026-10-21 |
| k1-anonymous-login-password | 匿名账号登录密码稳定性 | ClientLoginPassword、匿名登录、杀进程、密码指纹 | NK-10861 | Android8536新增三轮真实匿名密码认证经服务端确认同值；密码单项通过；游戏入场1通过2失败，iOS未测 | [匿名密码档案](k1-anonymous-login-password/experience.md) | 2026-11-02 |
| k1-throne-war-king-skill | 国王技能与城堡技能弹窗 | 王座战、禁锢、UIPlayerCityInfo、UIThroneWarKingSkill | NK-10866 / CS-305229 | 按用户指定原录屏城堡弹窗复验；技能使用与ESC正常，三语说明裁切；未通过 | [国王技能档案](k1-throne-war-king-skill/experience.md) | 2026-11-03 |
| k1-svs-cross-map-switch | SVS跨服V1/V2地图切换与传送 | SVS、跨服王座战、跨服入侵战、ThroneCross、WMapTarget、MapSwitch | NK-10910 / dev_NK-10910（仅客户端） | Unity标题级7用例通过（V1↔V2互跨、敌服迁城、回本服、ESC、本服迁城）；V2敌服焦土可落点极小为服务端风险；超时恢复与其他跨服场景未回归 | [SVS地图切换档案](k1-svs-cross-map-switch/experience.md) | 2026-11-04 |
| k1-save-egg-mail | 巨龙前置迁移补偿邮件 | SaveEgg、345、60010003、RoyalChest、版本迁移、防重 | NK-10875 / dev | Unity九项实现回归通过；完整产品规则待确认；只修既有模板ID无需机械三语 | [龙蛋邮件档案](k1-save-egg-mail/experience.md) | 2026-11-03 |
| k1-fte-version-switch | FTE版本与开关会话 | FTEVerGroupCfg、SwitchID、BeginSession、OPENING_CG、Generation、UIGuid | NK-10720、NK-10748、NK-10909 / dev、NK-10915 | 最终d96：正常SDK双向首次切服5→1、冷启/同服重登/真实ESC，9条定向通过；含可选开场键和旧会话回调修复；完整需求待确认 | [FTE会话档案](k1-fte-version-switch/experience.md) | 2026-11-05 |
| k1-first-charge | 首充三日购 | FirstCharge、UIFirstCharge3dayNew、Ver1首充、克劳蒂亚spine、Hero_Spine_207_GiftBag、fly00 | NK-10604 / dev（c23f9d12、17e9cc94） | 601 Unity：删spine后当前玩家（Old/分组101）首充弹窗与HUD入口正常；Ver1展示位空、标题仍为克劳蒂亚（600已存在，开关213服才可见）待经办人确认；含三套首充界面路由与残留引用排查法 | [首充档案](k1-first-charge/experience.md) | 2026-11-12 |
| k1-hero-treasure | 英雄秘宝 | 秘宝、TreasureRoot、UITreasureMain、奖励版本、setrewardver、NewHeroUI 349 | NK-10994 / dev（38d33514） | 602 Unity：奖励版本≥1 时新版英雄详情与背包秘宝入口显示、版本0隐藏，通过；新版英雄界面需开关349 | [秘宝档案](k1-hero-treasure/experience.md) | 2026-11-18 |
| k1-radar-one-click-dispatch | 雷达一键派遣 | 情报站、ExploreAtlasBatchCompleteReq、AtlasDispatchTroop 329、AP 未派遣原因 | NK-10951 / dev（7ca914ce10） | 602 Unity+协议直发4用例通过（体力预扣、连点不重复、AP原因）；客户端未适配AP原因提示待确认 | [雷达派遣档案](k1-radar-one-click-dispatch/experience.md) | 2026-11-18 |
| k1-skin-ui | 皮肤（装扮）界面 | UIShopSkin、喜欢、未拥有筛选、城堡【新】、SetSkinFavorite、ClearSkinNew | NK-10777（NK-10786/10787）/ dev | 602 Unity未通过：城堡【新】客户端未接服务端，重登丢失；喜欢/筛选/二次进入/三语布局正常；俄语「Нет」、阿语属性标题字形为待确认/既有问题 | [皮肤界面档案](k1-skin-ui/experience.md) | 2026-11-18 |
| k1-fte-guides | FTE版本选择与新手引导 | D2NewGuide、首次三选一、UIEnhanceCard、OPENING_CG、服段重叠 | NK-10903 / dev | Unity5通过1失败；重复14301消除、自然101完成/二次防重和强化详情真实ESC重开通过；FTE版本重叠及OPENING_CG自然错误仍在，标题基线待确认 | [FTE引导档案](k1-fte-guides/experience.md) | 2026-11-04 |
| k1-red-envelopes | 红包与每周领取限制 | RedEnvelope、Maxtimes、城堡等级红包、跨端依赖、真实拒绝瞬态取证 | NK-10873（配表）、NK-10874（服务器） / dev | 旧生成误归因更正保留；实际150成功/151拒绝、0不限151实领、独立性及收尾闭环；10用例7通过3未通过/2项显示问题；标题级、周切未验 | [红包验收档案](k1-red-envelopes/experience.md) | 2026-11-03 |
| k1-lord-equipment-box | 领主装备自选箱、BP与礼包 | LordEquipment、3320276、BP109550 | NK-10650、NK-10646 / dev | 601 Unity三语说明裁切、俄语标题重叠；正常一箱兑换/重登、BP两轨箱2/5到账及礼包箱20预览已核，轨0负例/测试订单履约及生命周期仍有缺口 | [领主装备箱档案](k1-lord-equipment-box/experience.md) | 2026-11-12 |
| k1-custom-avatar | 自定义头像与SDK更新 | 自定义头像与SDK更新 | NK-10333 / dev | Unity系统头像切换、回包、回显、权威回读、恢复及真实ESC共5通过；无本人已有自定义图，原单自定义缓存修复待补，原生上传链本轮范围外 | [自定义头像与SDK更新](k1-custom-avatar/experience.md) | 2026-11-04 |
| k1-hero-selectors | 英雄自选列表统一 | 英雄自选列表统一 | NK-10643、NK-10654 / dev | Unity六入口、真实发奖、普通/景观回归、英俄阿及ESC已核；12断言11通过1失败，混排普通道具白图缺数量，在线未通过；完整文档确认仍缺 | [英雄自选列表统一](k1-hero-selectors/experience.md) | 2026-11-04 |
| k1-alliance-honor-stars | 联盟荣誉之星滚动展示 | 荣誉星、19星、日月星、自动往返、StarLevelInfoWidget | NK-10895 / dev | Unity显示范围6断言通过；真实19星滚动、5/18星居中、刷新、英阿适配及真实ESC重开已核，勋章恢复0；未扩展为历史奖励争议通过 | [荣誉之星档案](k1-alliance-honor-stars/experience.md) | 2026-11-04 |
| k1-server-error-handling | 服务端错误日志处理 | NK-10757、error日志、ImmeUse、LegacyAutoUse、sender、GetPathsV2 | NK-10757 / dev | 阶段进行中：13 passed / 28 blocked / 2 pending，保留partialExecution；普通PvE首杀1→39及正常治疗已取证，PATH/MAP目标分支未通过；新轮保留数据续验 | [错误日志档案](k1-server-error-handling/experience.md) | 2026-11-04 |
| k1-client-compilation | 客户端编译与SDK依赖 | CS0234、TGS.SocketIO、tgs.basic、UPM、ALLUSERSPROFILE | NK-10906 / dev | 正式合入及Config/I18N#1336后Unity真实脚本编译/程序集加载1断言通过；需求文档确认标记待复核，资源及游戏业务另验 | [客户端编译档案](k1-client-compilation/experience.md) | 2026-11-04 |
| k1-hero-deployed-equip-red | 未上阵英雄装备武器红点 | 未上阵、主将、副将、红点、349、353 | NK-10923 / dev | Unity标题范围7用例通过；独占测试开关解阻后实测并恢复，完整需求待确认 | [英雄装备红点](k1-hero-deployed-equip-red/experience.md) | 2026-11-12 |

新增功能按 [档案模板](../assets/feature-experience-template.md) 创建 `features/<featureId>/experience.md` 并登记在本表；同功能改名、换分支或新一轮验收更新原档案。泛称“矿工”“特殊设备”“迷雾”或“首杀”只作为搜索线索，按需求确认归属。出生与迷雾专项和大地图主档案相互链接，同一分支不自动合并不同范围的结论。


每个功能的可复用脚本保存在该目录的 `scripts/`，先读其中 `usage.md`；没有适用脚本的档案明确注明，不创建空脚本目录。历史报告及原始回执留在原批次目录，Skill 只保存可追溯摘要与必要模板。以上状态都是历史批次的范围记录，不是本轮验收结论。
