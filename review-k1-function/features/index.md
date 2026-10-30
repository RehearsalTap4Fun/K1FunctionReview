# 功能验收经验索引

按名称、别名、关联需求或分支找到档案后，执行 [经验读写规则](../references/feature-experience.md)。只读取本次相关档案；更新时间是档案维护时间，不是业务重新验证时间。

| featureId | 功能 | 别名 / 搜索词 | 关联需求 / 历史分支 | 历史证据范围 | 档案 | 更新日期 |
|---|---|---|---|---|---|---|
| k1-kvk-sea-world | KVK海底世界 | 王座、KVK4、独立地图、85模板、匹配隔离 | NK-10712、NK-10714、NK-10707、NK-10715、NK-10735 / dev | 独立地图/真实归属前置已验证；缺真实85模板，上下文不能替业务验收 | [KVK海世界档案](k1-kvk-sea-world/experience.md) | 2026-10-29 |
| k1-lava-cave | 熔岩洞穴与科技扣费 | LavaCave、AP、批量科技升级 | NK-10750 / dev | Unity正常合法扣费、资源不足无副作用、单升/批升预算旅程通过 | [熔岩洞穴档案](k1-lava-cave/experience.md) | 2026-10-29 |
| k1-strongest-trial | 强者试炼 | type151、CommonScoreRank、白金兑换券、紫箱 | NK-10648 / dev | Unity真实奖励预览与1194000分入榜前态；双榜邮件自然End仍待验 | [强者试炼档案](k1-strongest-trial/experience.md) | 2026-10-29 |
| k1-commerce-shops | 次元商店与兑换商店 | UIMergeShop、TFWTab、头像框券、城堡预览 | NK-10651、NK-10644 / dev | 次元商店最小购买、三语及真实ESC重进闭环；兑换商店历史适配问题和人工完成决定分开保留 | [商业商店档案](k1-commerce-shops/experience.md) | 2026-10-29 |
| k1-arena | 竞技场 | ArenaV2、阵容快照、重复挑战、积分分档匹配、三语与多图反馈 | NK-10402 / dev_NK-10402；NK-10371、NK-10459（已发MR，599排除） | 10/27历史21项保留；10/29原32/33未合dev误纳入，技术实测仅开发参考，不计599通过/失败、不移挂其他项 | [竞技场验收档案](k1-arena/experience.md) | 2026-10-29 |
| k1-gold-miner | 黄金矿工 | GoldMiner、Gold Miner、矿工、挖矿活动、特殊设备、矿工币、ESC、返回键、HUD | NK-8062 / dev_NK-8062 | 玩家体验、反馈与运行片段；含 MuMu 连续帧普通输入体验（4–18 关通过，含标记目标优先、每局免费炸弹、钻石补体力及规则文案歧义），返回键后 HUD 消失仍待复验，非全功能通过；10/29追加实例GM/跨服排行隔离前置只读核证 | [黄金矿工验收档案](k1-gold-miner/experience.md) | 2026-10-29 |
| k1-world-map-rework | 大地图重构 | WorldMapV2、V2Fort、FogLayer、新大地图 | NK-8604 / dev_NK-8604 | 多批次静态预检；历史阻断待复核 | [大地图重构档案](k1-world-map-rework/experience.md) | 2026-10-21 |
| k1-first-day-fog-spawn | 新服大地图出生与随机迁城首日迷雾一致性 | 首日迷雾、D0 出生区、随机迁城、FogLayer | 2026-08-11 专项请求；相关 NK-8604 / dev_NK-8604 | 静态可进入运行验收；未执行运行验证 | [出生与迷雾档案](k1-first-day-fog-spawn/experience.md) | 2026-10-21 |
| k1-alliance-bi-recommendations | 联盟 BI 推荐场景 1–5 | 联盟BI推荐、union_bi_rec、BI 干预、AI 盟主、付费邀请 | NK-8728 / dev_NK-8728 | 静态预检及配置快照；历史阻断待复核 | [联盟 BI 档案](k1-alliance-bi-recommendations/experience.md) | 2026-10-21 |
| k1-hero-bonds | 羁绊系统调整 | 英雄羁绊、HeroBondMech、羁绊战斗机制 | NK-8953 / dev_NK-8953 | 静态预检；Mock 与真实链路待复核 | [羁绊档案](k1-hero-bonds/experience.md) | 2026-10-21 |
| k1-treasure-wear | 宝藏磨损度 | KingdomTreasure、Wear、王国宝藏磨损、最低磨损记录 | NK-8946 / dev_NK-8946 | 静态预检及生成 JSON 辅助检查；未运行 | [宝藏磨损度档案](k1-treasure-wear/experience.md) | 2026-10-21 |
| k1-cold-server-recruitment | 冷库服与召集活动调整 | 冷库迁服、冷库召集、ColdServer、coldsrc、UnionCross | NK-9710 / dev_NK-9710、dev | 历史全功能矩阵保留；10/29追加真实空列表、三语与原生ESC闭环，发布详情夹具另记缺口 | [冷库服档案](k1-cold-server-recruitment/experience.md) | 2026-10-29 |
| k1-google-play-achievements | Google Play 成就接入 | Google Play 成就、CPE 成就、CpeTask、LittleGameAchievement | NK-8028 / dev_NK-8028 | 0 完整通过、8 部分、24 阻塞、8 待 Android | [Google Play 成就档案](k1-google-play-achievements/experience.md) | 2026-10-21 |
| k1-radar-monster-first-kill | 雷达怪物击杀计数优化 | 普通雷达怪、雷达规则更新、选级、攻击、首杀隔离 | NK-9973、配套 NK-9974 / dev_NK-9973 | 1 通过、3 部分、20 阻塞；真实战斗未闭环 | [雷达怪物档案](k1-radar-monster-first-kill/experience.md) | 2026-10-21 |

新增功能按 [档案模板](../assets/feature-experience-template.md) 创建 `features/<featureId>/experience.md` 并登记在本表；同功能改名、换分支或新一轮验收更新原档案。泛称“矿工”“特殊设备”“迷雾”或“首杀”只作为搜索线索，按需求确认归属。出生与迷雾专项和大地图主档案相互链接，同一分支不自动合并不同范围的结论。

每个功能的可复用脚本保存在该目录的 `scripts/`，先读其中 `usage.md`；没有适用脚本的档案明确注明，不创建空脚本目录。历史报告及原始回执留在原批次目录，Skill 只保存可追溯摘要与必要模板。以上状态都是历史批次的范围记录，不是本轮验收结论。
