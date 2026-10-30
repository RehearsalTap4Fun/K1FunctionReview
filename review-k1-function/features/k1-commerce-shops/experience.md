# 次元商店与兑换商店验收经验

featureId：k1-commerce-shops。关联 NK-10651、NK-10644，2026-10-29 Unity 版本日补验。历史结果不能替代本轮验证。

## 再次验收先看

区分已加载资源、真实业务扣奖、普通页面旅程和多语言显示。次元商店从合并商店正常入口进入，兑换商店还受整服开放周期约束；先核当前实际规则，不复用旧日期。头像框兑换发的是待使用券，hasOwn=false 与券仍在包中并不矛盾。

## documentBaseline

- status：needs_review。
- source：https://jira.tap4fun.com/browse/NK-10651 、https://jira.tap4fun.com/browse/NK-10644 ；本次已读取资料保存在下述私有 S1 批次。
- confirmedVersion / confirmedAt：无完整静态对齐确认，不补造。
- currentVersion / checkedAt：2026-10-29 本轮 plan-new-environment.json 文档基线；未把版本表时间当需求版本。
- nextAction：复用前核本轮原需求及版本差异；本档案仅保存运行方法和历史现象。

## 来源

S1：FunctionPreview/.tmp/k1-599-supplement-20261029/commerce-runtime/，2026-10-29；client 529503dad1638e8b5d159c2ce6fd9d1b8bef1d8c、server 242b2db3eb2a3d206a17e491da7ed4283dbce235、config f904ffa7a7a9dc55f5173e71b7a3ed3216ffd263、生成客户端 f19a56c9d7dda8b1a4ba726d024e5b0512a24168。原图、身份、回执不随 Skill 分发。

## 已验证操作方法

下列条目均为 2026-10-29 / S1 的已验证方法；具体账号、实例、费用和授权每轮重核。

| entryId | 方法与完成信号 | 边界及下次动作 |
|---|---|---|
| commerce-loaded-bytes | 实读 IsUseBytesConfig 与新增商品关键值，再对正常页面 | 磁盘导入不等于运行时已加载 |
| commerce-real-click | 控件可能同时挂空 Button 和实际 EventTriggerListener.onClick，按真实注册监听执行 | 空 Button 调用无效是驱动问题，先核监听再判断产品 |
| commerce-tab-click | TFWTab 正常 OnPointerClick 才触发切页业务 | 仅设 isOn 不证明实际页已切换 |
| commerce-top-popup | 框兑换后自动 UsePrompt 要先正常处理，再继续下一页 | 覆盖层下调用底层控件不算完整玩家旅程 |
| commerce-frame-voucher | 正常兑换扣款、券增量、已拥有排序、重登持久化分别核验 | 未使用券不等于奖励丢失；已拥有分支不再弹兑换确认 |
| commerce-language-flow | 设置页语言 Toggle 与行 Click→正常确认→重启→核同一实际角色和语言 | 不直接伪造语言缓存 |
| commerce-screenshot-frame | CaptureScreenshot 后等实际渲染帧并逐图打开 | 截图工具可能同名写 JSON，额外资产状态文件应独立命名 |
| commerce-glyph-boundary | 看实际原图并投影实际字形顶点核裁切；英语可与阿语、俄语结果不同 | RectTransform 越屏本身不足以证明字形裁切 |
| commerce-esc-focus | 原生 Escape 未进入 Input、Application.isFocused=false 且键盘采样为空时记输入能力阻塞 | SendEvent/SimulateKeyBack 不代替真实键盘；不可凭弹窗未关判产品失败 |
| commerce-online-images | 当前 DOM 图片缩略可能是 div[src]；读取实际 DOM 后普通 locator.click 可打开在线预览 | 不猜旧 tab.cua 能力；表全局图片索引不等于单格数量；追加后逐图打开确认保留 |

## 本批业务观察

次元商品119正常单次兑换及三语显示通过；兑换框105正常扣款、发券与重登持久化通过。早期两项均缺本批实际 ESC 输入证据。2026-10-29 20:38（北京时间）已补齐次元商店真实ESC及重进，次元商店本项闭环；兑换商店由原表人工保持完成，本次未重开，其独立UI/ESC历史证据边界不改写。

S2：同一私有批次 `case47-native-esc-verified-results.json`、`arena-root/eligible47-native-esc-*-data.json` 及原尺寸截图。

| entryId | 方法与完成信号 | 边界及下次动作 |
|---|---|---|
| commerce-esc-native-recovered | 实际Unity窗口GameView空白区原生点击后核appFocused=true；Sky原生Escape关闭次元整店且CITY HUD保持。正常重进、普通119详情后Escape仅关详情，再Escape关整店；购买量119前后均1，没有再购买。 | 仅ESC缺口补验，原入口/点击/状态采集仍走Unity MCP；不因EditorWindow.Focus或发送键盘工具成功就声称收到输入。下一轮仍先核实际焦点。已验证2026-10-29/S2。 |

兑换商店有两项独立界面问题：底部说明在阿语约3px、俄语约17px被裁，计同一问题；俄语框108长标题与关闭按钮重叠约22px为另一问题。英语对应页面未复现。原始依据见 S1 的 receipt48-ui-ar-final.json、receipt48-ui-ru.json 及对应原图。再次验收重看实际修订画面，不将历史缺陷直接判为当前失败。

## 脚本与留存

暂无脱离本轮身份绑定并逐字验证的通用业务脚本，执行副本保留 S1。原始证据仍被本轮台账及补验依赖，未删除。2026-10-29 新增本档案并登记索引。
