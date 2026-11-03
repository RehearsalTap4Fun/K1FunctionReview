# 巨龙前置迁移补偿邮件

## 适用范围与历史结论

NK-10875，2026-11-03版本600，仅用户指定Unity路径。Client42c4667d、Serverba9bb524、Config1d42a49c下9项实现回归通过：当前版本阴性对照、旧版正常登录迁移、真实邮件内容、迁移新态、本封领取和重复请求、重登防重、独立已领奖测试状态、既有邮件显示与ESC。原单只有标题/版本提示，完整产品规则仍待确认；不能继承为以后版本通过或完整需求确认标记。

私有证据批次：`.tmp/k1-600-2904-20261103/reports/NK10875-mail-2904`及相邻回包/存档文件。原始邮件ID、账号、GM请求及录音不随Skill分发；每轮重新绑定目标实例、SID和自控角色。

## 修复与显示影响

本次修复取ConstConfig10135267的实际值作为旧有邮件模板60010003，而非把常量配置行ID作为邮件模板ID。只修已有邮件的业务发送链、不改文案/布局时，按[语言影响规则](../../references/ui-language-and-screen-adaptation.md#判断显示影响与检查范围)记“不需要”，不因打开邮箱验证就机械新增三语；本批此前已经取得的三语证据保留。

## 必要前置与缓存初始化

SaveEgg开关345须核实际服务端状态。`InitSaveEggMgr`在开关OFF载入时跳过私有配置/通知回调初始化，后来仅开关ON或普通重登不保证旧缓存重新初始化；不能直接在该对象上调用SwitchStage尝试夹具。

先让自控备用角色正常离线，等待自然LRU卸载后在345开启状态正常加载。门槛为离线且距max(LastAccessTs,LastLogoutTs)严格超过20分钟，再等保存扫描；不要用改时间、RemovePlayerNotSave或直接改DB代替。GetPlayer/PlayerGM会touch空闲时间，等待期间使用精确Mongo投影或经核实的RangeActivePlayer无touch观察。正常载入后先做当前版本阴性对照，再离线构造受守卫旧存档，确认持久化后正常UI登录触发迁移；禁止直接repair/PlayerOnline/发邮件冒充业务。

## 实际邮件与领取证据

通过HUD实际MailButton→系统箱TabTag4→真实邮件ID选中详情。仅按实际selfHead.mailCfgID识别60010003；标题会随语言变化，不能作为稳定键；没有加载完整列表也不能断言没发信。正常UI详情会标已读，先留未读前态。

真实协议为Mail2NdHeadListReq/Ntf、Mail2NdContentReq/Ntf、Mail2NdAttachmentReq/Ack/Ntf。首次只领取目标一封，不点全部领取；helper会抑制已领请求，验证服务端防重时可对同一实际ID发普通重复AttachmentReq，并分别核回包、已领标志和资产。重登核模板对应的ID集合，不以总邮件数代替。

4904001的Class=item_royal_chest；已解锁时正常自动使用会扣普通道具，再加到RoyalChestMgr.ChestBag[4904]。因此AssetNtf中普通4904001为0不代表漏发；应核皇室宝箱4904增量和另一附件21111001增量。权威存档`royalchestmgr.chestbag`；客户端现有缓存`RoyalTreasureChest.RoyalTreasureChestMgr.I.FullData.chestBag`，通知RoyalChestUpdateNtf。RoyalChestQueryReq在未解锁时可能初始化并发初始物品，不能描述为无副作用纯读。

## UI操作与证据可靠性

实际行数据类是`UI.UIMailItemDataNew`，不是UI.Mail命名空间。详情`pageData.md.IsRight`可能已缓存为true，但UI仍在异步加载；截图前还须检查loadingObj隐藏、正文/附件实际出现，并单独看稳定截图。语言或角色切换前注销本轮协议观察器，采用白名单避免保存认证消息；只保存真实收发/解码证据，不造回包。

64位任务/邮件ID跨工具保存为十进制字符串；原始Mongo文本或C#ToString保持精度。Go字段经Lua桥可能变成浮点数，不能用其与I64的跨类型等号当精确身份守卫；操作参数可用I64，精确大ID在新鲜权威原文中独立核对，Lua另校验目标角色、SID、版本、任务cfg/状态和领奖标志。

## 收尾与后续

保留正常领取、战斗和迁移结果，不以恢复为由重复发奖或覆盖已领真实进度。服务器临时开关按原实际状态恢复，并经正常重登核客户端；本批345/354最终OFF、中文、观察器注销。GM旧态夹具是显式一次性测试状态，不称自然历史存档，不直接复用绑定账号的私有脚本。完整产品规则确认后再决定原需求结项。
