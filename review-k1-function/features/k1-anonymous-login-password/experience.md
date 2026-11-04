# 匿名账号登录密码稳定性验收经验

featureId：k1-anonymous-login-password。关联：NK-10861。更新/实际验证日期：2026-11-02，Asia/Shanghai。实际版本：Android 1.0.600 / 8536；服务端/配表SHA未知。

## 再次验收先看

历史结果只限下列范围，不代表新一轮已通过。先核对实际设备、匿名userType、账号身份指纹、角色ID与SID，保留数据覆盖安装；不卸载或清档。原单截图报告为iOS，Android实测不能替代iOS。

documentBaseline.status=needs_review。来源：本轮用户提供的NK-10861完整截图，未做三端预检确认；当前图像哈希见私有运行baseline.json。无confirmedVersion或precheckRunId。

|entryId|方法/现象|状态/适用范围|验证日期/来源|下一动作|
|---|---|---|---|---|
|anon-sdk-fingerprint|adb logcat按当前应用PID采集；在SDK的InitAndLoginV3/Platform Anonymous参数行提取实际Password，在本机做完整SHA256；另记录匿名账号身份SHA256。严禁将真实密码或整段认证日志贴到聊天、反馈单或共享经验。|已验证，Android8536调试日志|2026-11-02，R1|核对新版日志格式；仅长度相同不足以证明值相同。|
|anon-lifecycle|force-stop后确认无PID，重新启动取得新PID，重新登录同一角色，比较全值指纹并在设置页核对SID/玩家ID。账号页返回重开、HOME恢复后，可只打开绑定选项触发SDK当前参数重新取样，随后关闭，不执行新绑定。|已验证，Android8536；三轮客户端密码一致|2026-11-02，R1|取样必须晚于操作时间，不可用旧日志充当新取样。|
|anon-evidence-boundary|本次SDK完整匿名客户端密码指纹一致；游戏网关AuthReq日志只含userType/长度，未取得最终请求或服务端密码全文。|已验证的证据限制|2026-11-02，R1|核实渠道q3kxs优先级后的最终AuthReq/服务器指纹，再给网关最终密码结论。|
|anon-auth4|第二轮冷启动出现平台认证失败(4)，客户端密码指纹未变化；界面重新连接后恢复同角色。登录时另见FTEVerGroupCfg版本区间重叠Exception，可忽略继续。|现象已验证，根因待验证；不归因为密码变化|2026-11-02，R1|保留首次失败，查询同期网关/平台认证日志并重测。|
|anon-ui-await|快速批量点击时0.8秒等待不足，导航漂移到战斗页并有误触。改为每步至少2秒且逐页核对后，本轮返回/后台项重新完成；等待秒数只是本次条件，不作未来固定保证。|已验证的自动化注意事项|2026-11-02，R1|按可观察UI完成信号推进；未知页面停止，不能盲点后续坐标。|

## 来源

R1：FunctionPreview/reports/nk10861-android-8536-20261102/summary.html、test-notes.md；FunctionPreview/.tmp/nk10861-device-20261102/保留原图、截图、指纹、计划台账和私有日志。不随Skill分发；其他机器需重新取证。

## 范围和收尾

本轮单台Android定向测试，未进行Unity/iOS或三语界面改动验收，不声称完整验收通过。无GM、部署、改密、清档或付费。安装及游戏自然进度保留；导航误触可能影响站位，前后图留存，不按猜测回滚。反馈未在线写回，原始证据有后续调查和本地校验依赖，继续保留。

## 脚本

本轮取证脚本绑定了设备与运行目录，仅保存在私有运行目录；暂无适合共享的独立无身份模板。复用方法时必须改为当前授权设备及本轮参数。


## R2：2026-11-02 服务端日志补证更正

以用户提供的查询结果7行请求参数为新证据，覆盖约16:00:31至16:12:57（北京时间）。16:00:53.875 AuthorizeAnonymousPOST及16:00:54.296 user=anonymous的AuthorizePOST各1次，二者密码指纹与本机SDK基线一致。三轮冷启动分别在16:07:46.204、16:09:48.458、16:12:57.371使用refresh_token，均没有password。

**anon-lifecycle、anon-sdk-fingerprint的结论仅限客户端缓存密码读值一致；SDK传参打印/AUTH_SUCCESS回调不能证明发起带密码的网络认证。不得再将三轮冷启动描述为三次匿名密码认证。** 反复打开绑定选项只用于本地读值取样，不证明服务端收到密码。

第二轮错误4紧邻令牌认证请求，现有文件不含响应或验证结果，不能断言令牌失效或密码变化。服务端保存的密码稳定性和重新提交密码认证仍未覆盖。补证未再次操作手机、退出/清档或撤销令牌。

entryId：anon-server-token-coverage；状态：服务端请求路径已验证，最终认证/存储密码仍待验证。来源：FunctionPreview/.tmp/nk10861-server-log-20261102/server-reconciliation.json、reports/nk10861-android-8536-20261102-server-reconciled/server-correction.md。原用户文件及凭证只保留私有路径，不随技能分享。


## R3：2026-11-02 三轮真实匿名密码认证及服务端独立确认

entryId：anon-explicit-ui-auth，方法已验证于Android8536。通过设置→账号→切换账户→使用本地账号登录，触发真正的`/tgs/auth2/authorize/anonymous` POST及后续`/authorize`，而非只打开绑定选项或冷启动使用refresh_token。全程同UUID/同K1账号，含中途force-stop，无清档、卸载、改密码或手工撤销令牌。操作前逐页核对，来源R3。

本轮新增三轮，服务端匿名接口与密码Authorize的北京时间分别是16:41:41.054/16:41:41.703、16:55:07.189/16:55:07.735、17:01:17.027/17:01:17.961。用户提供15行服务端记录，新增3次AuthorizeAnonymousPOST和3次带password的AuthorizePOST，六处完整密码指纹与16:00:54初始基线一致。真机HTTP完成与Anonymous PrivateAuthorize success=True也逐轮具备。**Android本轮匿名密码稳定性单项通过；R2所述重复密码认证证据缺口在此范围内已补齐。** 不等于直接查询过数据库存储密码，不覆盖iOS或清档/新账号。

entryId：anon-gateway-after-password-auth。三轮中第一、第三轮匿名平台认证成功后仍发生游戏网关平台认证失败，正常重连未恢复；第二轮进入同角色，身份已回读。整体入场1通过、2失败，不能将密码单项通过扩展成整链通过。收尾另有登录超时与ErrCodePfLoginFail，手机回桌面且账号角色数据保留，未宣称最终在线。根因待验证，下一步对齐失败请求的游戏网关认证/角色认证服务端响应。

来源R3：FunctionPreview/reports/nk10861-android-8536-reauth-20261102/summary.html、test-notes.md、server-new-confirmation.json、password-verdict.json；私有运行证据FunctionPreview/.tmp/nk10861-reauth-20261102-1635/。不保存真实密码、令牌或历史操作授权。与旧批次区分，不把同一账号日志/许可带到下一轮。
