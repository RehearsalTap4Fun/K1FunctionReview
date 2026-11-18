# 皮肤（装扮）界面：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-skin-ui |
| 名称 / 别名 | 皮肤界面、装扮；UIShopSkin、ShopSkinTabMenu、ShopSkinFilterBar、ShopSkinLocalState、SetSkinFavorite、ClearSkinNew、城堡皮肤【新】、喜欢、未拥有筛选 |
| 关联需求 / 分支 | NK-10777 皮肤界面优化（子单 NK-10786 客户端 / NK-10787 服务器）；相关 NK-10778 皮肤升级、NK-10779 圣诞皮肤 |
| 档案更新时间 | 2026-11-18 Asia/Shanghai |
| 最近实际验证 | 2026-11-17 602 版本日 Unity 路径；client dev@b2af6843、server dev@de2bda47（704c2786）、config dev@0ab12feb；本人 2605 |
| 维护源 / 在线地址 | 当前本地文件 |

## 再次验收先看

- 城堡【新】标记要跨登录验证：获得后不点开就重登，再看红点是否还在，并核对服务端 SkinInfo.isNew（见 SK-NEW-RELOGIN）。只在同一会话里看红点消失会漏掉问题。
- 喜欢走服务端持久化，重登后核对。
- 历史结论不等于本轮结果。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | needs_review（待复核） |
| source | NK-10777 Jira 描述「优化现有外显展示，让同屏展示的皮肤数量更多，优化展示逻辑」，无策划文档链接 |
| confirmedVersion | 空 |
| confirmedAt / precheckRunId | 空 |
| currentVersion / checkedAt | 未读取 |
| evidence | 无 |
| reason / nextAction | 取得策划文档后对齐补写 |

## 来源与版本

| 来源ID | 日期 / 批次 | 需求版本 / 三端版本 | 文件或文档定位 | 验证层级 / 可访问情况 |
|---|---|---|---|---|
| V602-NK10777 | 2026-11-17 / v602-20261117-jiangzhenyu-AI | client b2af6843、server de2bda47、config 0ab12feb | 本地运行目录 `FunctionReview/.tmp/k1-v602-20261117/evidence/nk10777/report.md`（不随 Skill 分发） | Unity 路径运行 + 三语；真机未覆盖 |

## 需求、代码与配置入口

| entryId | 入口 / 线索 | 用途及下次核对动作 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| SK-SERVER | 服务端 `ctl_skin.go`：SetSkinFavorite（持久化喜欢）、ClearSkinNew（清除【新】）；`.claude/docs/feature/skin.md` | 改喜欢/【新】时核对客户端是否真的发这两个请求 | 已核源码 | 2026-11-17 V602-NK10777 |
| SK-CLIENT | 客户端 `ShopSkinFilterBar.cs`（静态 `_tab`、筛选）、`ShopSkinLocalState.cs`（`FilterUnowned`，注释「喜欢、【新】以服务器 SkinInfo 为准」）、`ShopSkinData.UpdataIsHasInfo` | 反射读页签与筛选状态 | 已核源码 | 2026-11-17 V602-NK10777 |

## 环境与前置准备

| entryId | 条件 / 准备方法 | 完成信号及副作用 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| SK-ENV-GM | door `addskin <pid> <skinId>` 构造新获得（602 用永久城堡 1300/1301），测完 `removeskin <pid> <skinId>`；喜欢测完取消 | 服务端 skin 记录删除、喜欢恢复 | 已验证：2605 | 2026-11-17 V602-NK10777 |

## 操作方法与结果判断

| entryId | 前置 / 入口 / 参数 | 完成信号 / 异常处理 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| SK-OP-ENTRY | 主界面头像 `Mask/Head_k1` → `UiPlayerMain` 的 SkinBtn → `UIShopSkin`；页签节点 `Content/tab1..7`；筛选 `SkinFilter/BtnUnowned`，喜欢 `SkinFilter/BtnLike` | 页签：场景/城堡/行军/城堡幻化/聊天气泡/城堡称号；网格每行 3 张 | 已验证 | 2026-11-17 V602-NK10777 |
| SK-OP-LANG | `TFW.Localization.LocalizationMgr.SetLocalizationLanguage("en"/"ru"/"ar"/"cn")` 后重进 Play 并重登，再打开皮肤城堡页截图；结束切回原语言并回读 | 文本以 Editor 实际显示为准 | 已验证 | 2026-11-17 V602-NK10777 |

## 界面改动与三语验收

NK-10777 改布局、筛选与喜欢文案，判定为完整三语。

| 批次 / 构建版本 | 界面 / 状态 | 语言 | 设备 / 分辨率 | 显示观察 / 结论 | 截图 / 缺口与下一步 |
|---|---|---|---|---|---|
| v602 / b2af6843 | 城堡页默认、未拥有筛选 | en/ru/ar | Unity Editor | 布局无截断/重叠，阿语 RTL 镜像正确；见 SK-RU-UNOWNED、SK-AR-TITLE | 本地运行目录 lang-*.png |

## 反馈文档与字段准备

版本日验收走 K1 版本日必进项表（602 页签），无单独反馈表。

## 结果归档与过程文件清理

| 批次 / 需求 | 已回读结果与附件的稳定位置 | 归档 / 清理清单 | 已删过程文件数量 | 保留依赖 / 缺口与下一步 | 核验时间 |
|---|---|---|---|---|---|
| v602 / NK-10777 | 在线表第 19 行「未通过」已回读；未通过播报已发送 | 未清理 | 0 | 等修复后复验，运行目录保留 | 2026-11-17 |

## 历史问题、易漏场景与失效经验

| entryId | 现象 / 易漏场景 | 结论边界 / 下次动作 / 替代条目 | 状态 / 适用范围 | 验证日期 / 来源 |
|---|---|---|---|---|
| SK-NEW-RELOGIN | 城堡皮肤【新】客户端只用会话内 `ShopSkinData.isNew`（登录初始化为 -1），不读服务端 SkinInfo.isNew，点选也不发 ClearSkinNewReq；获得后不点开就重登，红点消失但服务端仍为新 | 602 判未通过（经办人张冰阳、李升旭、唐诗源）；复验时按「获得 → 不点 → 重登 → 看红点 + 服务端 isNew → 点选 → 看服务端是否清除」走一遍 | 已验证：602 存在 | 2026-11-17 V602-NK10777 |
| SK-RU-UNOWNED | 俄语「未拥有」筛选复用键 avatar_frame_time_none，显示「Нет」（无/否），语义弱于英文「Not owned」 | 待确认翻译，不计入 602 结论 | 待确认 | 2026-11-17 V602-NK10777 |
| SK-AR-TITLE | 阿语预览属性区标题「拥有属性/使用属性」（Skin_own_buff_desc/Skin_use_buff_desc）字形错乱，显示串被二次字形处理；Title1/Title2 预制体与赋值代码最近改于 NK-4524（2026-03） | 既有问题，建议另行跟进 | 已验证：602 存在 | 2026-11-17 V602-NK10777 |

## 可复用脚本

暂无通用模板。本轮切语言+重登+截图脚本在运行目录 `tools/lang19.sh`、`setlang.cs`，绑定了本人账号和运行目录。

## 更新记录

| 日期 / 批次 | entryId / scriptId | 新增、修订或失效原因 | 依据 / 未闭环事项 |
|---|---|---|---|
| 2026-11-18 / v602-20261117-jiangzhenyu-AI | 全部 | 首次建档 | SK-NEW-RELOGIN 待修复复验；真机路径未覆盖 |
