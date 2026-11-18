# SVS 跨服 V1/V2 地图切换与传送：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-svs-cross-map-switch |
| 名称 / 别名 | SVS、跨服王座战、跨服入侵战、ActvTypeKingWarCross=23、ThroneCross、V1/V2 地图切换、WMapTarget、MapSwitch |
| 关联需求 / 分支 | NK-10910 / client dev_NK-10910（MR !4059，仅客户端）；server/config 无同名分支，沿用 dev |
| 档案更新时间 | 2026-11-04，Asia/Shanghai |
| 最近实际验证 | 2026-11-04 功能验收，Unity 路径（真机范围外）；client 2b7ab07、server dev@88096b3d、config dev@fe77da53；标题级基线 7 用例全部通过（titleScopedAccepted），完整需求待确认 |
| 维护源 / 在线地址 | 本地文件 |

## 再次验收先看

- Jira 只有标题+3句描述，按标题级基线；地图版本、王座坐标、焦土规则均来自代码/配置“按实现验证”，不是策划确认规则。
- 必须两台服：V2 = SID 2914–2921（`New_Server_Map` Status/DevStatus 均为 "2914-2921"，地图类型首启落库锁定），V1 = 其他 SID。V1 王座 (3510,3510)，V2 王座 (3600,3600)。
- 服务端跨服时只下发 `SceneTypeKingWar`，不告诉客户端目标是 V1/V2；客户端按目标 sid 查开关自行判定（`WMapUtil.TryResolveTargetVersion`）。
- 历史结果不等于本轮验收结论；环境、账号、GM 授权每轮重新确认。

## documentBaseline

| 字段 | 内容 |
|---|---|
| status | needs_review（basisType=jira_title） |
| source | Jira NK-10910 标题与描述 |
| confirmedVersion | 无 |
| confirmedAt / precheckRunId | 无 |
| currentVersion / checkedAt | jira:NK-10910@2026-11-04T16:55:16.000+0800#sha256:c77775c3f97a92dd / 2026-11-04 17:05+08 |
| evidence | 私有运行目录 jira-NK-10910.json |
| reason / nextAction | 无策划文档；如有 PRD 需补对齐（焦土可落点范围、超时恢复弹窗交互） |

## 来源与版本

| 来源ID | 日期 / 批次 | 需求版本 / 三端版本 | 文件或文档定位 | 验证层级 / 可访问情况 |
|---|---|---|---|---|
| S-01 | 2026-11-04 nk10910-20261104-unity | 标题基线；client 2b7ab07 / server 88096b3d / config fe77da53 | FunctionPreview/.tmp/nk10910-20261104（plan/state/evidence），reports/nk10910-20261104-unity | Unity 实测；本机私有，不随 Skill 分发 |

## 需求、代码与配置入口

| entryId | 入口 / 线索 | 用途及下次核对动作 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| SVS-CODE-01 | client `LCrossServer`（WMapTarget、SwitchBatch、InteractionReady、15/30/10s 超时恢复）、`WMapUtil.TryResolveTargetVersion/TryGetHomeVersion`、`MapDelayInitMgr`、`CityTeleportManager`（_pendingAreaCoord/SwitchBatch 防旧回调） | Editor.log 中 `[MapSwitch] batch/target/phase` 与 `[WMap] Home=...HomeVersionSource` 可直接作 runtime 证据 | 已验证正常路径；超时/失败恢复分支未触发 | 2026-11-04 S-01 |
| SVS-CODE-02 | client 入口 `UIActivityThroneWarfareWar.OnClickThroneBtn` → `SendServerSwitchReq(KingWar, sid)`；回本服 `UIMain2.crossServerGoHomeObj`（弹“确认返回本服？”） | 正常 UI 入口 | 已验证 | 2026-11-04 S-01 |
| SVS-SRV-01 | 落城校验 `wmap/ctl_map.go GetRelocateCoord`：跨服 KingWar 玩家必须落 `manor.Black`，且不在 `IsInKingThroneZone`；V2 焦土 = `WorldMapV2UnitXZ` Type=3 五个点（王座+4哨塔）各占一个 15×15 领地格（ManorLen=15000） | V2 敌服可落点极小（实测哨塔格角落如 3644,3644 可落；3660,3600 等画面焦土被拒 BlackOut） | 风险观察，属服务端/配置，非本单客户端改动 | 2026-11-04 S-01 |

## 环境与前置准备

| entryId | 条件 / 准备方法 | 完成信号及副作用 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| ENV-01 | 部署两台本人测试服（自定义代码配表分支启动个人远程服，空服不导入，ALIVE 5）；V2 选 2914–2921 未被他人占用的 SID | 读 `ResolveLocalWorldMapKind`/`local world bind V2` 日志确认地图类型；SID 若复用旧库会带旧时钟（2915 旧库时钟 2027-03-10，偏移约+126天） | 已验证；先 `timeget` 两服再开局 | S-01 |
| ENV-02 | door telnet GM：`172.20.90.39:23200`（door sid=200，MakePort(2,3,200)）；`use game <sid>` / `use match 1` 后直接下 GM，一行可用 `|` 串多条 | 可在多服毫秒级连续执行，避开报名竞态；可对匹配服下 `exportkingwarmatch`/`kingwarmatch`/`importkingwarmatch` | 已验证（只读+本轮授权写） | S-01 |
| ENV-03 | 开局：两服同一行执行 `kwsync 3075 <UTC日期> <UTC时间>` + `actv newActvWithStartTs 3075 <ms>`（StartTs 取两服当前游戏时钟+5~6分钟）；两服 group 不同（2606=9，2915=10）也会被配成一组（StartTs 远在匹配服真实时间之后时） | `kwmatchcheck 1` 显示 match:[A B]、到点 status=Battle；客户端可能同时有旧的 type23 实例，`KingWarActivtyId` 会绑到已结束那期，需用进行中活动 id 打开面板 | 已验证 | S-01 |
| ENV-04 | 时钟对齐：只前推不回拨，`timeset <yyyy-MM-dd> <hh:mm:ss>` 在落后服执行（`synctime` 无参报错可忽略） | 整服影响，需授权；不可逆 | 已验证 | S-01 |
| ENV-05 | 账号：平台服列表不含 2914/2915，无法在 Editor 建角；V1 新服在登录页“所有服务器”点 SID 建角。V2 服用库里 UNITY_EDITOR 平台的旧测试角色 Dev 快速登录（fastlogin 模板 Toggle3=Dev）；结束后关 `K1D2Config.IsFastLoginDev` | 新角色需 `setroguelvl <pid> 71`、`settrainlv <pid> 15`（大地图需引导完成且主城≥10）、`create_test_union`、`addasset <pid> item 11114417 N` | 已验证 | S-01 |

## 操作方法与结果判断

| entryId | 前置 / 入口 / 参数 | 完成信号 / 异常处理 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| RUN-01 | 跨服前往：`UIActivityMain.Open(activityId)` → 实时战况 → 敌服王座“前往” | SwitchServerAck Success → SceneSwitchNtf(KingWar, sid, 王座坐标) → `[MapSwitch]` target version 与目标 SID 一致、resource=WorldMapV2/main、phase=Complete；ViewCenter=王座坐标 | 两方向均通过 | S-01 |
| RUN-02 | 敌服迁城：`CityTeleportManager.TryStartTeleport(pos)` → 弹窗 ui4124PopupCityTeleportation “使用” | 绿圈(CanTeleport=True)后才点使用；TeleportCityAck Success + 主城坐标回读；红圈原因用 `MapMgr.IsIntersectWithObstacle`/ObscaleManager.TouchMc 排查 | 已验证 | S-01 |
| RUN-03 | ESC：`Main.SimulateKeyBack()`；面板打开时关闭面板，世界地图无弹窗时无变化（本服对照一致） | 前后记录根 Canvas、cross/scene/ready/mapClick | 已验证 | S-01 |
| RUN-04 | 清弹窗脚本必须先记录文本、避开 `Ui_MessageBox` 中的业务确认框（如“确认返回本服？”），否则会误点取消 | — | 教训 | S-01 |

## 已知问题与风险

| issueId | 现象 | 状态 |
|---|---|---|
| RISK-V2-BLACKLAND | V2 敌服画面上大片焦土，但服务端只认 5 个 15×15 格；玩家按提示在可见焦土选点多被 ErrCodeCannotTeleportBlackOut 拒绝 | 待策划/服务端确认（非本单客户端范围） |
| GAP-RECOVERY | 15s/30s/10s 超时恢复弹窗、加载失败重试未触发验证 | 标题未规定，待确认后补验 |
| GAP-OTHER-SCENES | 本单把 KVK/DragonWar/LB 等跨服场景的重载统一改由新场景分支调度（needReloadMap=false），本轮未回归 | 建议回归 |

## 运行脚本

本轮使用的 door telnet、探针、迁城尝试脚本绑定本轮 SID/PID，仅存私有运行目录；快速登录复用 `../k1-giant-snake-phase4/scripts/fastlogin-dev.sh.txt`。
