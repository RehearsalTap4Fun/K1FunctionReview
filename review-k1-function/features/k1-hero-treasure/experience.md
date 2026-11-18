# 英雄秘宝：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-hero-treasure |
| 名称 / 别名 | 英雄秘宝；秘宝、Treasure、HeroTreasure、TreasureRoot、UITreasureMain、Treasure_System_Unlock_Infom（不是「宝藏磨损度」k1-treasure-wear） |
| 关联需求 / 分支 | NK-10994（缺陷：新服纪事完成后英雄详情和背包不显示秘宝）/ client 修复 38d33514，dev 合并 4d8ae408 |
| 档案更新时间 | 2026-11-18 Asia/Shanghai |
| 最近实际验证 | 2026-11-17 602 版本日 Unity 路径；client dev@b2af6843、server dev@de2bda47、config dev@0ab12feb；本人 2605 |
| 维护源 / 在线地址 | 当前本地文件 |

## 再次验收先看

- 秘宝入口（新版英雄详情右上角、背包「秘宝」页签）602 起看奖励版本 `VersionRewardMgr.currentVersion >= 1`，不再看纪事 1018。
- 新版英雄界面受开关 349 NewHeroUI 控制（dev 范围 2759-5000），本人 dev 服默认走旧版 `UIHeroUpgradeOld`，要先开开关再重登（见 HT-ENV-349）。
- 历史结论不等于本轮结果。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | needs_review（待复核） |
| source | NK-10994 只有标题和修复提交说明，没有独立需求文档 |
| confirmedVersion | 空 |
| confirmedAt / precheckRunId | 空 |
| currentVersion / checkedAt | 未读取 |
| evidence | 无 |
| reason / nextAction | 秘宝系统未经过预检文档确认；下次有秘宝需求时按原文档对齐后补写 |

## 来源与版本

| 来源ID | 日期 / 批次 | 需求版本 / 三端版本 | 文件或文档定位 | 验证层级 / 可访问情况 |
|---|---|---|---|---|
| V602-NK10994 | 2026-11-17 / v602-20261117-jiangzhenyu-AI | client b2af6843、server de2bda47、config 0ab12feb | 本地运行目录 `FunctionReview/.tmp/k1-v602-20261117/evidence/nk10994/report.md`（不随 Skill 分发） | Unity 路径运行；真机未覆盖 |

## 需求、代码与配置入口

| entryId | 入口 / 线索 | 用途及下次核对动作 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| HT-GATE | 客户端 `HeroTreasureUnlock.cs`（解锁判断）、`UIHeroDetailWnd.cs`（Root/TreasureRoot 显隐）、`HeroTreasureBagPageReference.cs`（背包秘宝页签）；条件为奖励版本 ≥1 | 改秘宝入口时先看这三处是否用同一判断；旧版 `UIHeroUpgradeOld` 602 未改 | 已验证：dev 602 | 2026-11-17 V602-NK10994 |

## 环境与前置准备

| entryId | 条件 / 准备方法 | 完成信号及副作用 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| HT-ENV-349 | door `changeswitch <pid> 349 on` 后重登；测完 `changeswitch <pid> 349 off`（内存开关，下次登录生效） | 英雄列表进入 `UIHeroListNew` → `UIHeroDetailWnd` | 已验证：2605 | 2026-11-17 V602-NK10994 |
| HT-ENV-REWARDVER | door `setrewardver <ver>`：整服奖励版本，客户端实时收到 `RewardVersionNtf`；会把 RewardVerTs 写成当前时间，并触发配置重载和在线玩家礼包检查。测完改回原值 | 只在本人独占服使用，并记录留存的 RewardVerTs | 已验证：2605（原值 18） | 2026-11-17 V602-NK10994 |

## 操作方法与结果判断

| entryId | 前置 / 入口 / 参数 | 完成信号 / 异常处理 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| HT-OP-DETAIL | 新版英雄列表 → 任一英雄详情 → 右上角秘宝 2×2 格 | `Root/TreasureRoot` activeInHierarchy=True；点击打开 `UITreasureMain` | 已验证 | 2026-11-17 V602-NK10994 |
| HT-OP-BAG | 主界面右侧 `Scroll View/BagBtn/BagBtn/Button` → `UIShop`。注意右侧另一个 MergeShopBtn 是次元商店，不是背包 | 页签为 特殊/背包/秘宝；版本 0 时只有 特殊/背包 | 已验证 | 2026-11-17 V602-NK10994 |

## 界面改动与三语验收

NK-10994 只改入口显隐，没有新增或修改文案，多语言判定为「不需要」；不涉及 Gameplay HUD，ESC 不适用。

| 批次 / 构建版本 | 界面 / 状态 | 语言 | 设备 / 分辨率 | 显示观察 / 结论 | 截图 / 缺口与下一步 |
|---|---|---|---|---|---|
| v602 / b2af6843 | — | 不需要 | Unity Editor | 无文案改动 | — |

## 反馈文档与字段准备

版本日验收走 K1 版本日必进项表（602 页签），无单独反馈表。

## 结果归档与过程文件清理

| 批次 / 需求 | 已回读结果与附件的稳定位置 | 归档 / 清理清单 | 已删过程文件数量 | 保留依赖 / 缺口与下一步 | 核验时间 |
|---|---|---|---|---|---|
| v602 / NK-10994 | 在线表第 24 行「已完成」已回读；报告在本地运行目录 | 未清理 | 0 | 整轮未结束，运行目录保留 | 2026-11-17 |

## 历史问题、易漏场景与失效经验

| entryId | 现象 / 易漏场景 | 结论边界 / 下次动作 / 替代条目 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| HT-OLD-UI | 本人 dev 服不在开关 349 范围内时，只能看到旧版英雄界面，容易误判「秘宝入口不显示」 | 先确认实际走的是哪套英雄界面 | 已验证 | 2026-11-17 V602-NK10994 |

## 可复用脚本

暂无。本轮探针（读 TreasureRoot、读背包页签）绑定了本人账号和运行目录。

## 更新记录

| 日期 / 批次 | entryId / scriptId | 新增、修订或失效原因 | 依据 / 未闭环事项 |
|---|---|---|---|
| 2026-11-18 / v602-20261117-jiangzhenyu-AI | 全部 | 首次建档 | 真机路径未覆盖 |
