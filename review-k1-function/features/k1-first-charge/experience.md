# 首充三日购：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-first-charge |
| 名称 / 别名 | 首充三日购；首充、FirstCharge、FirstRecharge、UIFirstCharge3dayNew、Ver1 首充、克劳蒂亚 GiftBag spine、Hero_Spine_207_GiftBag、fly00 |
| 关联需求 / 分支 | NK-10604（快速任务：删除克劳蒂亚 spine）/ c23f9d12（2026-10-14，已进 hotfix_client/1.0.600 和 qa）、dev 合并 17e9cc94（2026-11-11，补删 fly00_SkeletonData.asset） |
| 档案更新时间 | 2026-11-12 Asia/Shanghai |
| 最近实际验证 | 2026-11-12 601 版本日 Unity 路径；client dev@534ebaa4（1.0.601）、config dev@7fdd86cb、server dev@343e9994；本人 2605 |
| 维护源 / 在线地址 | 当前本地文件 |

## 再次验收先看

- 首充有三套界面，入口由服务端下发的版本和分组决定，**先查玩家实际走哪套界面，再判断改动影响**（见 FC-ROUTE）。
- 删资源类改动在三端都要查残留引用：prefab/scene 的 GUID、配置表路径、代码读取方。确认引用方能不能被打开，再决定是判风险还是判失败（见 FC-STALE-REF）。
- Ver1 首充只在开关 213 覆盖的服务器出现，本人 dev 服通常不在范围内，没法用真实数据复现，需要在报告里说明。
- 历史结论不等于本轮结果。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | needs_review（待复核） |
| source | NK-10604 为快速任务，未取得独立需求文档 |
| confirmedVersion | 空 |
| confirmedAt / precheckRunId | 空 |
| currentVersion / checkedAt | 未读取 |
| evidence | 无 |
| reason / nextAction | 首充功能本身没有经过预检文档确认；下次有首充需求时按原文档对齐后补写 |

## 来源与版本

| 来源ID | 日期 / 批次 | 需求版本 / 三端版本 | 文件或文档定位 | 验证层级 / 可访问情况 |
|---|---|---|---|---|
| V601-NK10604 | 2026-11-12 / v601-20261111-jiangzhenyu-AI | client 534ebaa4、config 7fdd86cb、server 343e9994 | 本地运行目录 `.tmp/k1-v601-20261111/evidence/nk10604/report.md`（不随 Skill 分发） | Unity 路径运行 + 源码/资源静态核对；真机未覆盖 |

## 需求、代码与配置入口

| entryId | 入口 / 线索 | 用途及下次核对动作 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| FC-ROUTE | 客户端 `UI/FirstCharge/FirstChargeHelper.OpenAdaptively`：`FirstChargeNewMgr.I.useOld`（服务端 `forceuUseOld`）→ `UIFirstCharge`（MainCity/UIFirstCharge3day.prefab）；`isValid` → `UIFirstCharge3dayNew`；两者都不满足时 3 秒后重试一次。调用方：HUD 首充按钮 `UI/Main2/FirstCharge3Day/UIMain.FirstChargeThreeDay.cs`，商城 `GameBankPage.cs` | 判断当前玩家看到哪套首充界面 | 已验证：dev 601 | 2026-11-12 V601-NK10604 |
| FC-VER1 | `UIFirstChargeNew`（Activity/UIActivityFirstChargeNew.prefab）。只有开关 213 `FirstRechangeNew_1` 开启的服务器（2026-11 时为 1333、1335、1349、1351、1353–1378）注册、首充版本被定为 Ver1 且未完成的玩家才会看到。服务端版本分配在 `game/play/internal_play/ctl_first_recharge*.go` 和 `gdconf/conf_firstrechargeversionlist_ext.go` | 改 Ver1 展示或资源时，核对目标服是否在开关内，以及玩家实际版本 | 已核源码；Ver1 真实数据未复现 | 2026-11-12 V601-NK10604 |
| FC-NEWUI-LAYER | `FirstChargeNewUI.SetSpineOrImage` 读取 FirstRechargeNewCfg 的 asset_type=2/SpineiD，未判空；但它所在弹窗 `FirstChargeNewUI.Layer`（MainCity/UIFirstCharge3day_4）在代码里没有调用方。`UIFirstCharge3dayNew` 不读 SpineiD | 配置指向已删 prefab 时，先确认这一层是否仍不可达 | 已核源码：dev 601 无调用方 | 2026-11-12 V601-NK10604 |
| FC-ICEBREAK | `UI/TriggerGift/GiftDetailUI.cs` 的 IceBreakingRoot/Spine 只在破冰礼包（D2GiftCfg type=12）时激活 | 删 spine 后看 type=12 礼包数量；2026-11 为 0 个 | 已核配置 | 2026-11-12 V601-NK10604 |

## 环境与前置准备

| entryId | 条件 / 准备方法 | 完成信号及副作用 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| FC-ENV-OLD | 本人 dev 服新账号默认走新三日购：首充版本 Old、分组 101、未购买 → 自动弹出 `UIFirstCharge3dayNew` | 弹窗展示 SSR 尼萨拉，可切第一/二/三天；没有改服务器或存档 | 已验证：2605 | 2026-11-12 V601-NK10604 |
| FC-ENV-VER1 | Ver1 需要开关 213 范围内的服务器和对应注册数据，本人 dev 服不满足 | 只能做本地诊断渲染，不能当真实玩家路径证据 | 待验证 | 2026-11-12 V601-NK10604 |

## 操作方法与结果判断

| entryId | 前置 / 入口 / 参数 | 完成信号 / 异常处理 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| FC-OP-HUD | 登录后等自动弹出；关闭后点 HUD「首充」重开；切三天页签 | 界面栈出现 `UIFirstCharge3dayNew`，Editor.log 无 Exception/ERROR | 已验证 | 2026-11-12 V601-NK10604 |
| FC-OP-DIAG | 诊断旧界面或 Ver1 布局时用 PopupManager 打开，或临时实例化 prefab 截图，结束后销毁/关闭 | 没有 Ver1 数据时打开 `UIFirstChargeNew` 会自己关闭；`UIFirstCharge` 用反射关不掉，要点它的 CloseBtn。诊断打开只用于看布局，不算玩家路径证据 | 已验证 | 2026-11-12 V601-NK10604 |

## 界面改动与三语验收

NK-10604 只删资源，没有新增或修改文案，多语言判定为「不需要」；不涉及 Gameplay HUD，ESC 不适用。

| 批次 / 构建版本 | 界面 / 状态 | 语言 | 设备 / 分辨率 | 显示观察 / 结论 | 截图 / 缺口与下一步 |
|---|---|---|---|---|---|
| v601 / 534ebaa4 | — | 不需要 | Unity Editor | 无文案改动 | — |

## 反馈文档与字段准备

版本日验收走 K1 版本日必进项表（601 页签），无单独反馈表。

## 结果归档与过程文件清理

| 批次 / 需求 | 已回读结果与附件的稳定位置 | 归档 / 清理清单 | 已删过程文件数量 | 保留依赖 / 缺口与下一步 | 核验时间 |
|---|---|---|---|---|---|
| v601 / NK-10604 | 在线表第 12 行「已完成」已回读；报告在本地运行目录 | 未清理 | 0 | 运行目录保留，供经办人确认 Ver1 风险 | 2026-11-12 |

## 历史问题、易漏场景与失效经验

| entryId | 现象 / 易漏场景 | 结论边界 / 下次动作 / 替代条目 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| FC-STALE-REF | 删克劳蒂亚 spine 后，Ver1 首充 `Root/FirstRecharge/SpineRoot` 下只剩这一个 nested prefab，展示位变空，标题仍是「SSR 克劳蒂亚SSR」；旧 `UIFirstCharge` 的 HeroPage/SpineRoot 节点丢失（该界面本身还是 AAAA 占位文本）；FirstRechargeNewCfg 1001/1002（以及 custom_10 的 1001/1002/3001/3002）、D2HeroGiftCfg 6001/6002 仍指向已删路径；UIGuide_Task、UIGiftBag、UIShop(Legacy)、MapOffline_KvK.unity 仍引用已删 GUID，但这些 prefab 没有被引用 | 600 删资源时就存在，601 没有新引入；当前玩家路径不可达或无报错，判风险不判失败。Ver1 是否换图或改标题由经办人张冰阳确认；有新结论后更新本条 | 待经办人确认 | 2026-11-12 V601-NK10604 |
| FC-DELETE-CHECK | 删资源后要查：`find Assets -iname '*<资源名>*'` 无结果；prefab/asset/scene 里没有旧 GUID 和资源名文本；配置表路径和代码读取方逐个确认是否可达 | 查到残留引用不等于失败，看运行时能否走到 | 已验证方法 | 2026-11-12 V601-NK10604 |

## 可复用脚本

暂无。本轮探针（读取首充版本/分组、打开诊断界面、扫描残留引用）绑定了本人账号和运行目录，没有整理成通用脚本。

## 更新记录

| 日期 / 批次 | entryId / scriptId | 新增、修订或失效原因 | 依据 / 未闭环事项 |
|---|---|---|---|
| 2026-11-12 / v601-20261111-jiangzhenyu-AI | 全部 | 首次建档 | Ver1 风险待经办人确认；真机路径未覆盖 |
