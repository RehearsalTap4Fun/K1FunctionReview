# 熔岩洞穴与相关科技扣费：验收经验

| 字段 | 内容 |
|---|---|
| featureId | k1-lava-cave |
| 关联需求 | NK-10750（城市科技与熔岩洞穴扣费） |
| 更新时间 / 实际验证 | 2026-10-29 Asia/Shanghai；599版本日Unity |
| 版本 | 客户端529503da；服务器242b2db3；配置f904ffa7 |

## documentBaseline

status=needs_review；本档案未单独建立完整功能PRD确认标记。仅记录本次进包项正常扣费旅程，不能扩大为洞穴全功能通过。

## 可复用事实

来源 LAVA-599-E1：`FunctionPreview/.tmp/k1-599-supplement-20261029/case27-verified-results.json`、`backend/own-lava-virgin-open-once.json`、`arena-root/eligible27-lava-protocol.jsonl`；原始图片/角色/Key只保留本批次，不随Skill分享。

| entryId | 方法 / 成功信号 / 下次核对 | 状态 |
|---|---|---|
| LAVA-ENTRY | 正常底部Alliance菜单→实际LavalCave按钮；UnionItem是聊天入口。UIAllianceMain是SceneUI，不可按BasePopup查找。新盟可能先弹全局命名空间UIAllianceGift，按自身Close正常关闭。 | 已验证：真实正常入口 |
| LAVA-VIRGIN | 只在已核实自控、从未开始的棋盘用lavacave_open准备；memberregtime只改本人资格字段。开板后保留实际周期Start/Close，不用reset/settle/rank强结。后续isopen会改FirstOpen，需先重新审计Lava和其它活动窗口。 | 已验证：前置；禁止当通用重置步骤 |
| LAVA-COST | 正常相邻合法开板Ack0，AP12→11、贡献0→1；临时仅本人AP11→0，再正常相邻开板Ack3821，完整权威棋盘/AP/ATK/贡献及个人24榜原样；恢复夹具至AP11，保留真实1AP消耗。没过关/出口、没跨服23结算；不据此称所有结算通过。 | 已验证：本旅程扣费及失败无副作用 |
| CITY-TECH-COST | 本批自然碎片3：正常UpgradeSkill单升type2的0→1、碎片3→2；UpgradeSkillQuick请求再升3次，真实逐级成本1+2+2，余额只够一次，实际1→2、碎片2→1且成功Ack。必须按当前等级取成本并应用实际buff，不能误用目标等级成本。 | 已验证：本旅程单升/批升预算 |

没有通用可直接执行的运行脚本；固定身份的GM/探针仍在本批次。后续先重核棋盘、联盟归属、时间和个人资源，历史通过不代替本轮证据。
