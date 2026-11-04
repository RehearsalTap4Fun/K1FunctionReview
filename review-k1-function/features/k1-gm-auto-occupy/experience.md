# GM 自动占领：王座迁城实测经验

| 字段 | 内容 |
|---|---|
| featureId | k1-gm-auto-occupy |
| 名称 / 别名 | GM 自动占领、LGmAutoOccupy、王座禁迁、自动迁城 |
| 关联分支 | dev_NK-9557；本轮为用户定向修复与实测，非完整需求验收 |
| 更新时间 / 实际验证 | 2026-11-02，Asia/Shanghai；Unity 真实联网实测 |

## 再次验收先看

先核实实际登录角色、SID和地图模式。历史服务器分配及整服GM权限不继承。原始身份、回执与执行副本留在私有运行目录，不随技能分享。

## documentBaseline

status=needs_review。来源为本轮聊天的两个明确行为：打王座时迁到禁迁区外、迁完正常出兵。未取得独立完整策划PRD，不能据此宣称整套大地图验收通过。

## 方法与发现

| entryId | 方法 / 结论 | 状态与边界 |
|---|---|---|
| GAO-01 | GameReader.ReadTeleportForbiddenArea 必须覆盖原服V1和V2；不能只判 WMapUtil.IsWMapV2Active。V1使用 KingWarBuilding Type=1 的 CoordX/Y，V2使用 WorldMapV2UnitXZ BuildingId=5001 的 PositionTuple。KVK不套用本服矩形 | 旧版遗漏在本轮实测发现并补齐；V1迁城已联网通过，V2本轮未联网复验 |
| GAO-02 | 禁迁边长读 TerritoryUtils.ThroneRange → MapSizeCfg.throne_size。运行值60000换算60格边长、中心到边界30格；不可混用建筑8格占地或LOD的2×2领地显示范围 | 运行配置与服务端真实落点已核对。搜索仍需加主城占地半径及余量 |
| GAO-03 | 从远处启动 LGmAutoOccupy.StartRun，通过正常 TeleportCityReq；取 TeleportCityAck、Out/InNtf、主城最终坐标和道具差值共同验证；Ack成功不单独作最终证据 | 本轮真实迁城成功，落点在矩形及占地余量之外，消耗高级迁城道具1个 |
| GAO-04 | 迁城后NewTroopAck返回18062 / ErrCodeKingWarStatusErr时，继续核对ThroneWarCityInfo.actStatus与只读kwview，不能误归因为迁城/选点失败 | 本轮为ThroneActStatusNone，已实际发出出兵请求，但尚无成功出兵证据；待整服活动前置授权 |
| GAO-05 | kwview通过UI.UIGM.SendGMReq传显式目标SID。kwview无参数会被OnGMReq的最少参数检查拒绝。kwsync会重置王战模式并初始化活动，进入Battle会清理本期王座/哨塔争夺数据，不能按角色级GM对待 | 本轮仅kwview只读已执行；kwsync未执行，不能记录为已验证操作模板 |
| GAO-06 | 临时探针用MessageMgr.RegisterMsg监听TeleportCityAck、TeleportCityOutNtf、TeleportCityInNtf、NewTroopAck、NewLineupStateNtf及GMAck；清理时逐类Unregister并移除日志回调。保存并恢复SettingsCodec及原目标列表 | 本轮已清理并回读；Unity真实业务与107项EditMode回归分别留证 |

## 来源

2026-11-02 私有运行批次 `.tmp/throne-2903-20261102-1045/`；报告 `reports/20261102-2903-throne-teleport-awaiting-war/summary.html`。客户端HEAD `36cc1615f7aac182b95e3a3260d6aff88da0d284`加运行目录client-fix.diff；服务端部署SHA未取得。该批次迁城通过，出兵成功待整服王战前置，不沿用为完整通过。

## 运行脚本

本轮带身份绑定的probe-start.cs.txt仅在私有运行目录保存；没有经授权完整走通王战出兵与恢复前，不发布可复用的整服GM脚本。
