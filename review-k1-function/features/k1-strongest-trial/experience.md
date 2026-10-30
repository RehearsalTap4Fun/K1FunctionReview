# 强者试炼验收经验

featureId：k1-strongest-trial。关联 NK-10648；2026-10-29 Unity 版本日补验，只完成排名奖励预览及真实入榜资格前态，结束发奖未验。历史环境及授权不继承。

## 再次验收先看

本批旧活动 cfg109227/type151/content109215 与新拆分109586/109587不同。先核实际活动 ID、StartTs、归属、ServerVersion、内容及真实客户端入口。排名预览与真实结束发奖是不同证据，不能用前者关闭后者。

## documentBaseline

- status：needs_review。
- source：https://jira.tap4fun.com/browse/NK-10648 ，本轮可访问来源及文档基线保存在 S1。
- confirmedVersion / confirmedAt：无完整静态对齐确认，保持未知。
- currentVersion / checkedAt：2026-10-29 本轮 plan-new-environment.json 及后续不可变修订所列基线。
- reason / nextAction：档案记录运行方法；复用前核对当前需求及新旧活动差异，不把版本表更新时间当需求版本。

## 来源

S1：FunctionPreview/.tmp/k1-599-supplement-20261029/ 的 item50-root-actions.json、trial151/、trial151-child/、backend/p1-mail151-137-prestate-audit.md。client 529503dad1638e8b5d159c2ce6fd9d1b8bef1d8c；server 242b2db3eb2a3d206a17e491da7ed4283dbce235；config f904ffa7a7a9dc55f5173e71b7a3ed3216ffd263；生成客户端 f19a56c9d7dda8b1a4ba726d024e5b0512a24168。私有身份、原图、回执不随 Skill 分发。

## 方法与边界

以下均为 2026-10-29 / S1 已验证，参数及实际实例每轮重核。

| entryId | 方法和完成信号 | 边界及下次动作 |
|---|---|---|
| trial151-normal-entry | 正常活动选择→CommonScoreRankBanner 奖励入口→ActvRankListCommonAck→排行/奖励页及本跨服切换 | type151 不走 UIActivityGenericRankBanner；不能仅 ShowPanel 后写成正常活动入口 |
| trial151-version-rewards | 实读同 ServerVersion 的 VersionRewardMgr.GetDisplayRewards，并逐图核正常奖励页 | 本批紫箱21117003本服前三档2/1/1，跨服前三及4–10档10/8/5/3，仅适用本批配置 |
| trial151-rank-isolation | 用实际cfg与StartTs整秒构造tag，读取真正 Local/GlobalService 前缀、Rank42命名及版本规则；两个物理key均读TYPE/ZCARD/完整ZRANGE WITHSCORES | 新GS不等于全局排行隔离；不猜group前缀、不删共享key。先证明空或全成员自控，才产生分数 |
| trial151-normal-qualification | 经正常兑换双确认消费白金券，分开保存成本夹具、真实扣款、发券、ownedRow、行为积分Ntf和两榜Ack | 成本GM本身不算积分；本批199券正常消费后实际1194000分，不能把数量换算当实际入榜证据 |
| trial151-cache-refresh | 扣款后即时客户端活动分数缓存仍可能旧值；正常重入活动取得真实ScoreInfoNtf和两榜 | 未等正常回包前不把旧缓存判成不加分，也不手改缓存 |
| trial151-rank-ui-duplicate | 排行列表一条本人，底部固定self条再显示本人，结合raw rankList与完整Redis成员计数 | 不把底部self条误判为两条排行记录 |
| trial151-mail-prestate | MAIL2ND真正存储为目标游戏DB的mail集合，按本人playerid完整读取；实际live Sender队列需独立核 | actvmail仅saveAll落盘，集合为空不证明live队列空；不得调用标读/领取协议冒充纯读 |
| trial151-end-obligation | 预览、真实资格、完整邮件和每种附件库存前态分别留证；按实际Start+配置时长核真实End | 本批尚未跨End。不能用nextstate、强制发奖或预览替代自然截止后的邮件、附件、领取与防重 |

## 本批保留结论

本服和跨服实际各只有一名自控玩家、均第1，超过500000资格。完整邮箱为0、live sender无该玩家待发项，排名第一的五种附件资产逐项为0。根据已加载配置与冻结服务器调用链，预期本服与跨服分别进入10921501、10921502两封邮件，不合并；仍须实际End验证，不能视为已发奖。

当前没有脱离身份绑定并逐字复验的通用执行脚本；副本留 S1。所有证据仍有未来End及机器台账依赖，未删除。2026-10-29 新增本档案。
