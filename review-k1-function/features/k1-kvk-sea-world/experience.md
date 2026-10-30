# KVK 海底世界：运行环境与验收经验

| 字段 | 内容 |
|---|---|
| featureId | k1-kvk-sea-world |
| 关联需求 | NK-10712、NK-10714、NK-10707、NK-10715、NK-10735 |
| 更新时间 / 实际验证 | 2026-10-29 Asia/Shanghai；599版本日Unity |
| 版本 | 客户端529503da；服务器242b2db3；配置f904ffa7 |

## 再次验收先看

下述是环境验证经验，**对应业务尚未通过**。历史服务器、账号和许可不能复用为新轮授权。

## documentBaseline

status=needs_review；本档案没有独立功能PRD确认标记。原599行和本轮冻结玩家旅程仅作为任务来源，下轮读取实际PRD与原问题再对齐，不能从本环境经验推定完整需求已确认。

## 方法、限制和留存

来源 KVK-599-E1：`FunctionPreview/.tmp/k1-599-supplement-20261029/` 下 `backend/private-kvk-authoritative-scene.json`、`kvk-live-context-source/`、`arena-root/eligible01-cn-owned-throne-data.json`、`backend/private-kvk-shared-match-absent-after.json`；实际ID/角色/回执只保留原批次，不随Skill分享。

| entryId | 结论 / 下次动作 | 状态 |
|---|---|---|
| KVK-STANDALONE-SCENE | 现有kvk_setup_test、真实SetMatchResult及kvk_c能在本人独立battle生成持久化真实地图。MapType10032/nav9/npcRefresh5/tag4；“Map5”不能误写成实际MapType ID。以真实battle_scene、正常实体广播、渲染实体和普通地图点击核验，不以exec succ判成功。 | 已验证：仅独立地图夹具 |
| KVK-TEMPLATE-BOUNDARY | 独立地图ActvID=0不产生真实85活动的KvkUnionTmplInfoNtf。实际跨服场景成立而LPlayer.kvkTag仍0，会走旧详情，可能看到默认捐献/攻击按钮。缺有效模板时不能据此判真实海世界路径失败，也不能手写kvkTag或注入Ntf凑通过。先取得完整隔离的85活动/报名链。 | 已验证：上下文缺口；业务待验证 |
| KVK-SHARED-MATCH | 本批共享match实际版本92c8e7e3。真实85 OnStart/OnTick同步GS，GS再SyncKvkUnionStat2Match；新空tag也可能改变最近两届历史选择。只拥有独立game/battle不代表完整匹配隔离。未执行openkvk、全局Match配置或RecordTag写入。下轮按实际运行版本重新核。 | 已核源码与部署；共享操作未授权执行 |
| KVK-THRONE-FIXTURE | 注册kvkfort setowner可准备真实归属，冻结版本不发首占奖、不收赛季；仍会清争夺/驻军并更新领土、属性、任务与纪事。只能对已核实全自控场景操作。kvk_reduce会动全部未开放建筑，若还有早领窗口，应避免全量操作；本批仅对单个王座解锁截止准备，正常tick开放。GM归属不等于个人真实驻守时长。 | 已验证：前置副作用；正常占领/时长未通过 |
| KVK-ENTRY-CLEANUP | kvk_gm_enter_scene异步后，GS City字段可仍本服；真实battle日志、跨服客户端与实体需联合判断。配对leave后本批客户端已回本服/CITY且inWar=false、CN、观察器卸载；私有地图日志仍保留1个City/MapPlayer记录，不能宣称地图数据已删除。保留场景并披露，勿为清理擅自强End/删库。 | 已验证：客户端恢复；服务器夹具保留 |

没有可直接运行的通用造场脚本；本批辅助脚本含绑定身份，不分享为默认执行入口。三语、ESC、真正85生命周期及结算仍需完整活动前置。
