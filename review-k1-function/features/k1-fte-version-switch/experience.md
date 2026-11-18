# FTE版本与开关会话：验收经验档案

featureId：`k1-fte-version-switch`。别名：FTEVerGroupCfg、SwitchID、BeginSession、OPENING_CG。关联：NK-10720、NK-10748、NK-10909。维护时间2026-11-05（Asia/Shanghai）。最新提交d96c99dfacb7已完成正常SDK冷启、双向切服、同服重登与真实ESC；全部9条定向断言通过，完整需求基线仍待确认，原版本日结论不自动关闭。

## 再次验收先看

必须区分LSwitchMgr中按服计算的表值缓存、连接下发的服务器覆盖和本地GM覆盖。使用新LoginAck SID前不得复用旧服计算值；不能通过清掉服务器覆盖来“修复”表值缓存。检查冷启、双向自然切服、同服重连以及已完成引导状态，原进度保留。历史SID和GM权限不继承。

## documentBaseline

- status：needs_review。
- source：https://jira.tap4fun.com/browse/NK-10720 、https://jira.tap4fun.com/browse/NK-10909 。
- confirmedVersion / confirmedAt / precheckRunId：未知。
- currentVersion / checkedAt：2026-11-05只读回查原单仍无正文；未形成已确认完整需求基线。
- evidence：本机私有 `FunctionReviewRuns/fix-600-client-20261105/jira-source.json`，不随Skill分发。
- reason / nextAction：原单标题级来源；仅针对原未通过场景修复，完整规则待核。

## 来源与版本

S600-FIX：客户端dev基线`ee4e3aced8da`，候选修复的7个文件及哈希见本机私有`FunctionReviewRuns/fix-600-client-20261105/repair-status.json`。服务器/配表本轮未部署。`switch-regression.json`记录真实LSwitchMgr源码及FTE版本Resolver、模拟配置/消息适配器的隔离验证；不是Unity正常登录证据。

S600-FIX-RUN：同一私有目录runtime中的normal/stable-login、relogin-en-2650、fte-login-log-check与state。正式Mac转换#1338成功，修复客户端4ef019e1566a；用户明确分配的现存2650实例经过共享协调和身份核对后复用，无重建/导入/改时。服务器版本依上轮回执bf7d67与当前容器/进程复核，镜像GitCommit标签unknown，不冒称标签独立验证完整SHA。

S600-FIX-SUP：用户后来明确允许正常往返2914并恢复桌面。私有目录 `FunctionReviewRuns/fix-600-client-20261105/runtime/supplement-1334/final-session-guard`，正式报告 `reports/unity-recheck-final-20261105-1356`；最终client d96c99dfacb7、Mac转换#1340 SUCCESS/config bbb4e407d，运行前已核最新推送。两次中间自然失败分别保存在补验目录的residual-before-fix和stale-callback-before-fix，不以最终成功覆盖。补验无服务器GM、改时或部署，结束中文及本地入口覆盖恢复。

| entryId | 结论 / 方法 | 状态、适用范围与下次动作 |
|---|---|---|
| fte-prelogin-switch-cache | 真实源码+模拟配置复现：旧服计算345=false被缓存，改登录SID后第一次解析仍选范围版本3；按LoginAck SID清除计算缓存后选开关版本5。反向切服也需清理；服务器覆盖须保留 | 11项隔离回归通过。S600-FIX-SUP正常SDK角色按钮及确认，双向首次被动会话采样为2914版本5/2650版本1，稳定345自然开/关、均无覆盖；原2650完成引导/stage200及中文保持。未调用版本Resolver/BeginSession验证 |
| fte-session-before-data-init | GameData.Init及登录回调可能启动关卡/引导；FTE BeginSession应在目标配置组/SID已选定后、这些回调之前执行。会话未就绪时不得使用默认版本解析开场Key | 独立完整Editor编译通过；S600-FIX-SUP最终冷启、双向切服、同服重登及退出窗口FTE错误为0，覆盖2914未完成引导/stage0和2650完成引导/stage200；仅提前BeginSession不足以消除以下两类残余 |
| fte-optional-opening-key | OPENING_CG正式映射只有版本2/3/4，版本5无此入口。开场尝试、跟进及每步完成通知先HasConfiguredGuideKey，再严格解析实际目标，不能给缺入口版本硬补旧链或全局关日志 | 中间4ef真实2914版本5仍报missing OPENING_CG，769f加可选入口检查；5项隔离实际方法检查通过，d96最终自然登录无此错误。已配置但缺失/禁用的目标诊断保持；不改正式配置 |
| fte-deferred-ui-session | 旧UIGuid的下一帧Show/Restore和视频关闭回调必须绑定FTE Generation；会话结束或变化后，不能继续旧角色的UI步骤、完成标记、BI或地图拖动状态操作 | 769f真实切回时旧OnShown回调在server0尝试解析D2NewGuide911；d96校验初始化及Generation，旧视频清空待续引用后退出。4项隔离真实回调检查通过，最终同路径退出无FTE错误，完成角色进度保留 |

本次是缓存/会话逻辑修复，无文案布局变更，不机械增加三语。所用测试适配器仍是本轮私有一次性回归工具，无已验证的可分享业务运行脚本。运行证据和正式台账仍有后续复验依赖，未清理。
