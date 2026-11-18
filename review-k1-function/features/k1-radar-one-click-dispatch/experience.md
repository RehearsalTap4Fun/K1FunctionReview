# 雷达一键派遣：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-radar-one-click-dispatch |
| 名称 / 别名 | 雷达（情报站）一键派遣；ExploreAtlas、ExploreAtlasBatchCompleteReq/Ack、OneKeyDispatchBtn、AtlasDispatchTroop、AtlasExploreFailedReason、UIOneKeyDispatchTroopTips。雷达怪物击杀计数见 [k1-radar-monster-first-kill](../k1-radar-monster-first-kill/experience.md)，不同功能 |
| 关联需求 / 分支 | NK-10951（快速任务：雷达一键派遣 bug）/ server 修复 7ca914ce10，dev 合并 bb17c92ac5 |
| 档案更新时间 | 2026-11-18 Asia/Shanghai |
| 最近实际验证 | 2026-11-17 602 版本日 Unity 路径（含协议级直发）；server dev@de2bda47、client dev@b2af6843、config dev@0ab12feb；本人 2605 |
| 维护源 / 在线地址 | 当前本地文件 |

## 再次验收先看

- 一键派遣要四个前置：开关 329、情报站任务等级 ≥3、月卡、空闲队列里有英雄（见 RD-ENV）。缺开关时同一个请求会走旧的「一键完成」分支，回包类型都不一样。
- 客户端点击前会按全部未领奖任务的体力求和预检，体力不够直接弹行动力界面、不发请求。所以服务端的体力拦截分支只能直发请求来测（见 RD-OP-DIRECT）。
- 历史结论不等于本轮结果。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | needs_review（待复核） |
| source | NK-10951 只有标题和修复提交说明 |
| confirmedVersion | 空 |
| confirmedAt / precheckRunId | 空 |
| currentVersion / checkedAt | 未读取 |
| evidence | 无 |
| reason / nextAction | 下次有雷达派遣需求时按原文档对齐后补写 |

## 来源与版本

| 来源ID | 日期 / 批次 | 需求版本 / 三端版本 | 文件或文档定位 | 验证层级 / 可访问情况 |
|---|---|---|---|---|
| V602-NK10951 | 2026-11-17 / v602-20261117-jiangzhenyu-AI | server de2bda47、client b2af6843、config 0ab12feb | 本地运行目录 `FunctionReview/.tmp/k1-v602-20261117/evidence/nk10951/report.md`（不随 Skill 分发） | Unity 路径 + 协议级直发；真机未覆盖 |

## 需求、代码与配置入口

| entryId | 入口 / 线索 | 用途及下次核对动作 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| RD-SERVER | 服务端 `ctl_explore_atlas.go` 的 ExploreAtlasAutoMarch：按体力逐笔预扣，等刷怪回调的占位任务预留体力并占住队列，搜索失败清占位；全部被体力拦下回 ErrCodeAssetCountActionForce(3813)，未派遣原因 AtlasExploreFailedReasonAP(3) | 改派遣逻辑时核对预扣、占位、清占位三处 | 已验证：dev 602 | 2026-11-17 V602-NK10951 |
| RD-CLIENT | 客户端 `CollectAtlasTaskUI.cs`（点击前体力求和预检；OneKeyDispatchBtn 需 taskLevel ≥ EnergyAtlas_One_Click=3 且开关 329）、`OneKeyDispatchTroopTipsItem.cs`（按未派遣原因显示提示） | 602 客户端枚举只有 0/1/2，没有 AP(3) 分支 | 已核源码 | 2026-11-17 V602-NK10951 |

## 环境与前置准备

| entryId | 条件 / 准备方法 | 完成信号及副作用 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| RD-ENV | door：`changeswitch <pid> 329 on` + 重登（329 AtlasDispatchTroop，dev 范围 2854-8999）；`addeatlasexp <pid> 5`（任务等级 1→3）；`buygift <pid> 603`（月卡，测试通道）；`addD2Hero <pid> <heroId> 1`（新英雄自动编入空队列）；体力 `clearap` + `addasset <pid> recover 11171002 <N>` | 雷达界面出现「一键派遣」按钮。月卡、英雄、任务等级不可回退，记为留存 | 已验证：2605 | 2026-11-17 V602-NK10951 |

## 操作方法与结果判断

| entryId | 前置 / 入口 / 参数 | 完成信号 / 异常处理 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| RD-OP-DIRECT | Unity 内 `Common.MessageMgr.Send(new cspb.ExploreAtlasBatchCompleteReq())`；先用 `Common.MessageMgr.RegisterMsg` 注册只读回包监听（存到 AppDomain 以跨次执行读取），测完注销 | 以 Ack 的错误码、undispatched 列表和服务端日志 `ap not enough need=… remain=…` 判断；体力与队列状态回读 | 已验证 | 2026-11-17 V602-NK10951 |
| RD-OP-DOUBLE | 雷达界面同帧调用两次「一键派遣」按钮回调 | 第二次回 ErrCodeExploreAtlasAutoMarchErr，只有一支行军、体力只扣一次 | 已验证 | 2026-11-17 V602-NK10951 |
| RD-ACKERR | 控制台 `AckError NewTroopAck:1` 是服务端主动派兵导致 Ack 比 Req 多，不是错误码 | 不当成失败证据 | 已验证 | 2026-11-17 V602-NK10951 |

## 界面改动与三语验收

NK-10951 只改服务端，没有新增文案，多语言判定为「不需要」；不涉及 Gameplay HUD，ESC 不适用。

| 批次 / 构建版本 | 界面 / 状态 | 语言 | 设备 / 分辨率 | 显示观察 / 结论 | 截图 / 缺口与下一步 |
|---|---|---|---|---|---|
| v602 / de2bda47 | — | 不需要 | Unity Editor | 服务端改动 | — |

## 反馈文档与字段准备

版本日验收走 K1 版本日必进项表（602 页签），无单独反馈表。

## 结果归档与过程文件清理

| 批次 / 需求 | 已回读结果与附件的稳定位置 | 归档 / 清理清单 | 已删过程文件数量 | 保留依赖 / 缺口与下一步 | 核验时间 |
|---|---|---|---|---|---|
| v602 / NK-10951 | 在线表第 27 行「已完成」已回读；报告在本地运行目录 | 未清理 | 0 | 整轮未结束，运行目录保留 | 2026-11-17 |

## 历史问题、易漏场景与失效经验

| entryId | 现象 / 易漏场景 | 结论边界 / 下次动作 / 替代条目 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| RD-AP-TIPS | 客户端没适配未派遣原因 AP(3)：用真实回包调提示框，标题写成「以下部队因战力不足，无法派遣！」，条目同时显示 HP 和战力图标、数值为预制体占位「99.99M」 | 正常点击基本到不了（客户端预检拦下），记待确认，经办人张迪确认是否补客户端展示 | 待经办人确认 | 2026-11-17 V602-NK10951 |
| RD-SEARCH-FAIL | 搜索失败清占位（NpcId<=0 / SearchMapNotAdapt）是服务端自愈分支 | 602 未构造出搜索失败条件，未实测 | 待验证 | 2026-11-17 V602-NK10951 |

## 可复用脚本

暂无通用模板。本轮回包监听、直发请求、状态读取脚本在运行目录 `tools/hook27.cs`、`acks27.cs`、`send27.cs`、`state27.cs`，绑定了本人运行目录。

## 更新记录

| 日期 / 批次 | entryId / scriptId | 新增、修订或失效原因 | 依据 / 未闭环事项 |
|---|---|---|---|
| 2026-11-18 / v602-20261117-jiangzhenyu-AI | 全部 | 首次建档 | RD-AP-TIPS 待经办人确认；真机路径未覆盖 |
