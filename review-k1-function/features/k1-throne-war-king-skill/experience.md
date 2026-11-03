# 国王技能与城堡技能弹窗验收经验

| 字段 | 内容 |
|---|---|
| featureId | k1-throne-war-king-skill |
| 名称/别名 | 王座战、国王技能、UIThroneWarKingSkill、UIPlayerCityInfo |
| 关联需求 | NK-10866；原客诉CS-305229 |
| 最近验证 | 2026-11-03，版本600版本日验收，仅Unity；历史结果不代表下一轮结论 |

## 再次验收先看

必须读取原Jira全部字段（names+fields），复现步骤在customfield_12000、预期在customfield_10206、实际在customfield_10207；description空不代表只有标题。CS-305229原录屏实际是俄语大地图点击同盟城堡后的UIPlayerCityInfo；NK-10866自动生成正文却指向UIThroneWarKingSkill九技能列表。2026-11-03用户明确要求按原录屏城堡弹窗验收，二者不能混用证据。

## documentBaseline

- status: needs_review
- source: NK-10866自定义复现/预期/实际字段及CS-305229录屏；用户原录屏入口更正
- currentVersion: 543e5262b86cba42b4ae3bcdbf3ab8dfdeb33aa7651db17d569e1071b8f0fd37
- checkedAt: 2026-11-03
- confirmedVersion/confirmedAt/precheckRunId: 未建立预检确认标记
- nextAction: 保留原单正文与录屏入口差异；不得声称完整需求已预检确认。

## 稳定入口与关系条件

- 国王总览普通入口为主城KingHall→UIActivityThroneKingWar公告页Buttom/Btn3→UIThroneWarKingSkill；技能详情、使用记录是不同页签。
- 原录屏入口为大地图真实玩家城堡点击链→RMapEntityManager.clickActionDic[MapUnitPlayerCity]→OnClickPlayerCity→UIPlayerCityInfo；事件层MCP辅助导航不等于原生命中断言。
- `UI/Map/City/KillSkill/UIPlayerCityInfo.KillSkill.cs`：真实国王看非盟友有禁锢、拆除、掠夺神器；同盟隐藏禁锢，保留后两项；自己或非国王另有显隐条件。同盟隐藏禁锢不能直接归为列表未滑到底。
- 技能按钮直接发送KingSkillUseReq，不要盲点他人城堡。隔离测试服只用自有目标；Req、无错误Ack、UseNum变化分别留证。
- 服务端整数坐标除1000才是Unity世界坐标。必须用本轮实际实体owner/PID确认，不使用经过浮点舍入的大整数实体ID。

## GM夹具和副作用

- `kingskill 999 <本轮PID>`设置整服国王，可能触发称王事件、清理技能次数/日志/效果，不是仅改变UI显示权限。准备前核对本轮服务器归属、原KingID及副作用；不能继承历史SID/PID授权。
- `forcejoinunion <自有无盟PID> <精确unionID>`可准备同盟目标，走正常加入联盟逻辑；保留原无盟状态和留存变化。不要直接改客户端cityType/owner字段冒充关系。
- 不为清理误用kingskill 1，它会清整服技能；下次是否清理须按本轮独占范围和保留要求判断。

## 本轮运行证据与结论边界

Client42c4667d57ea893718bfe1bfed4ab830caa3eabc、Serverba9bb5246755912eaa70ed1e714c287d0acfce10、Config1d42a49cc9035ad4d4681016dd09ac25e0e893ae。Unity Client_Clone，2904专属服；真机用户明确范围外。

城堡弹窗8个独立断言：5通过、3失败。非盟友禁锢1007真实使用成功；同盟只显示拆除与掠夺神器；Unity原生ESC关闭后地图HUD正常且可重新进入。英语掠夺神器说明末尾被裁切；俄语两条说明preferredHeight220.5>rectHeight129.33；阿语153>129.33，均Truncate且没有ScrollRect父级。不得将这些运行结果归为九技能总览修复通过。

三语按正常头像→设置→语言→语言行→ChangeLanguage确认链切换，实际重启登录后核PID/SID，结束恢复cn。不要直改本地化字段或把语言重启当真实进程冷启动。

源表600行11已写未通过，K解释入口、关系和裁切差异；L同一单元格保留俄/英/阿三图，逐图在线打开核验，F下拉选项及颜色回读保留。原始证据在FunctionReview `.tmp/k1-600-2904-20261103`；发布报告`reports/NK10866-castle-2904.html/summary.html`由runtime_acceptance.py publish生成，完整需求fullyAccepted=false。publish的output参数是目录，即使名字以.html结尾也会在其下生成summary.html和runtime-result.json；引用前按实际文件核验。

## 附图操作经验

当前MCP读写值可用，`set_cell_range`的空对象跳过在本轮返回invalidRequest；改用最小单元格update_range并回读验证，不覆盖整行或图片。DWS本企业未暴露sheet media-upload，不能把命令列表中的理论能力当可用。

在线表格可用内置浏览器：名称框定位L11；首次剪贴板PNG粘贴进入空截图单元格，等待保存。双击图片单元格出现已有缩略图和“上传图片”，该可见按钮支持filechooser流追加图片并保留前图。插入菜单的首次filechooser监听不能替代真实写入验证。每图在线打开后保存截图，再用get_cell_infos核对richText图片ID数量。不要把编辑态空白当图片被删；以保存、权威回读和实际打开为准。

无独立可复用脚本；上述方法按下一轮实际界面核对。
