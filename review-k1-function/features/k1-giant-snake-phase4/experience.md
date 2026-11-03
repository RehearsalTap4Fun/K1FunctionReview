# 巨蛇大作战4期：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-giant-snake-phase4 |
| 别名 | 肉鸽塔防4期、巨蛇4期、Phase4Minion、混合无尽 |
| 关联需求 / 分支 | NK-10652、NK-10657 / dev_NK-10652 |
| 更新时间 | 2026-11-03，Asia/Shanghai |
| 最近实际验证 | Unity首轮85项：14通过、25失败、46阻塞（保留已测子分支）；18条事项待统一决策。小兵/盾/混合无尽接入未生效，不能称这些战斗类型已通过。 |

## 再次验收先看

先读取本轮私有台账中的 checkpoint、授权、计划与 next 队列，不重复询问已确认范围。历史实例、GM许可与部署不是下一轮授权。正式Excel、客户端加载值和服务器部署值分别核验；静态匹配不代表业务通过。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | needs_review |
| source | https://alidocs.dingtalk.com/i/nodes/7NkDwLng8ZMa3Y5aTpPpp724JKMEvZBY |
| confirmedVersion / confirmedAt | 尚未确认 |
| currentVersion | e43dd6227179640eef661a23ca66d00840b8d03a0dd9a12c476c70a466732667（Markdown正文SHA256） |
| checkedAt | 2026-11-02，Asia/Shanghai |
| evidence | S-01中的document-source.json、plan.json |
| reason / nextAction | 本轮用户明确要求存疑项先记、首轮实测后统一决策；不得倒填文档确认或回写原文。 |

## 来源与版本

| 来源ID | 批次与定位 | 层级与可访问性 |
|---|---|---|
| S-01 | K1FunctionReview/.tmp/k1-nk10652-20261102-unity；客户端21cf159a3edf48da49716ede0ccb154ab84c56f5、正式配置9f4436eb149816db6dbf4cde5c9260ac09fd3c78 | 本机原始证据，不随Skill分发；10份工作簿经Git LFS OID/大小校验，85项用例已编排，首局已实际执行但失败。 |

## 已核实的定位与待验证项

| entryId | 事实或方法 | 状态与下次动作 |
|---|---|---|
| CFG-LEVELS | ActivityDragonRoguelikeLevel.xlsx的ActDragonBattleLevelCfg为40普通关＋41挑战；布局24底部/16中心，10小兵关包含11/25两纯兵关。 | 2026-11-02静态核对；运行入口、解锁与胜负仍需实测。 |
| CFG-PROJECTILES | DragonRoguelikeSkill.xlsx的ActivityProjectileParams与客户端Phase4Projectiles.json需逐参数比较；当前水环baseHarm/appendBaseHarm为5.2/6.0与6.5/7.5两组。Phase4BeamRuntime.TryLoadSettings读TextAsset，Phase4RingRuntime消费settings.ring。 | 2026-11-02在S-01实际首局只读比较：导入表5.2/6.0，Active运行对象6.5/7.5（ring-runtime-parameters-first-battle.json）；实际命中伤害和正式导出映射仍待验证，禁止手工改生成配置。 |
| CFG-INSTANCE-GUARDS | Phase4MinionConfigStore、Phase4ShieldConfigStore、Phase4EndlessConfigStore按TextAsset.activityIDs检查实例。 | 静态核对；新活动开测先读实际实例ID，分别经正式入口验证兵/盾/无尽，预览成功不能替代。 |
| ENV-DEPLOYMENT | 同名服务端分支缺失时，可由真实Jenkins构建参数定位已部署代码与配置；最新dev和当前运行提交可能不同。 | 方法已用于只读核查；以本轮镜像、构建、实际配置交叉确认，不默默回退分支。 |
| TOOL-ASYNC-REFLECTION | EditorDebugMCP v0.1.0的invoke返回Task本体时，序列化器可能读取Task.Result并阻塞编辑器；本轮调用后编辑器无响应，根因尚待进一步验证。 | 避免返回Task本体；必要异步启动后链式读取IsCompleted等非阻塞值。无响应时保留状态并按本轮权限确认恢复，不能把连接注册当作可执行。 |
| RUN-SKILL-CLOSE | UIEnhanceSkill关闭时执行UIEnhanceSkillData.onCloseCallback；当前抽奖回调捕获UITowerDefenseSlotMachine.SetMaskState，必须关注父界面销毁后引用。 | 2026-11-02 S-01首局9%实际出现MissingReferenceException：SetMaskState:437 → OpenEnhanceUnitPopup回调:575 → UIEnhanceSkill.OnCloseStart:164。页面残留且World未Resume；证据skill-close-missing-reference.log、current-skill-page-check.png。后续版本须正常抽卡并关闭技能页复验，不能修回调后冒充原版本通过。 |
| RUN-CLOSE-EVIDENCE | ExecuteEvents返回true只证明存在事件处理器；BasePopup.Close会先清空关闭回调/出栈，后续异常可能保留可见对象。 | 2026-11-02 S-01实际验证：页面可见但PopupManager.FindPopup返回null，后续点击无效。观察器遇到同页重复须停止并取异常/生命周期证据，不能把重复页面都记成新开箱或持续盲点。 |
| RUN-SNAPSHOT-ISOLATION | SnapshotMgr.ContainsLastSaveData在UNITY_EDITOR等条件下跳过版本/角色匹配，活动存档目录按玩法前缀分隔，未按角色分目录。 | 2026-11-02 S-01只读存档头与实际提示一致；未恢复另一角色战局，不外推正式包。必要隔离时逐文件保留原路径、SHA256、时间戳并核验备份，验收收尾恢复；账号及原件仅在私有台账。 |
| RUN-ENTRY-PREP | 活动HUD入口仍受主线肉鸽进度与引导条件影响；现有setroguelvl玩家GM可构造主线开放前置，actv rtAddCard可添加活动卡，actv rtSetLvl构造活动关卡。 | 2026-11-02 S-01已验证主线开放、三种新卡添加、正常HUD入口及四卡自动补阵后Save/Start ACK成功；rtSetLvl已实测ACK并更新目标关卡，清除StartingInfo和目标及之后奖励；只用于场景准备，跳关不计自然通关。每次绑定本轮授权身份，IsRunning单一标志不足以防止战中GM，必须同时检查IsPlaying及玩法上下文。 |
| RUN-INSTANCE-GUARDS | 本轮正常进入3、4、11、41后，Minion/Shield/Endless的Active均为空，实际ActivityID不在各TextAsset白名单；三新弹道却按内容正常激活。 | S-01的level03/04/11/41-phase4-runtime.json及实图；不能写成所有四期功能都未启动，也不能把预览实例当成正式实例证据。相关深层断言保留具体依赖。 |
| RUN-GETALL-DEDUP | 全选锁仅禁用单卡，没有完整阻止全选再次提交；同帧正常pointerClickHandler两次均成功ACK，道具按两个梯度扣除，相同三词条各添加两次。 | S-01 russian-double-getall-protocol.jsonl及前后列表，已记录失败；未伪造网络请求。单次刷新/全选和资源不足结果须独立记录，不能被重复确认失败覆盖。 |
| RUN-PROJECTILES | 实测每组20枚游走弹，重叠施放可有40枚总数；环有同圆心追加和回流缩小，暂停时elapsed/radius冻结。 | S-01 three-projectiles-motion-analysis.json、ring-return-geometry-analysis.json；DTO缺少wave身份，不能用几何样本冒充逐目标命中次数或伤害公式验证。 |
| RUN-REVIVE | 正常自然失败后复活ACK成功、扣道具、已存在蛇回退；累计投放与强化保留，未发现HP补高。 | S-01 russian-revive-analysis.json；仅证明本轮蛇的观察范围，不能外推缺失的小兵、3/1调度、新积分、双源箱。 |
| RUN-HUD-CARD-LOOKUP | GamePlayEnhanceHeroItem.RefreshCdFill以活动卡ID查CDragonHero，实际每帧缺表错误；本轮另发生一次原生崩溃，managed栈含ExLog工作线程调用Unity日志。 | S-01 runtime-native-crash-preface.log与dump；错误与崩溃并存，不声称已证明因果。正常重启后续测，不自动改业务代码。 |
| RUN-LANGUAGE-RESTART | 现有语言流程SetLocalizationLanguage后Main.ReStart；可自动登录原角色，不一定出现选角页。 | S-01英/俄/阿均真实重进；先读实际身份/语言，避免因没出现选角页而重复登录或误判失败。收尾恢复原语言。 |
| RUN-RTL-LAYOUT | 阿拉伯语主活动倒计时和战斗伤害飘字出现水平镜像；结算长技能名压叠数值。英/俄/阿排行榜长标签越入横幅，刷新与全选余次共用“刷新次数”文案。 | S-01多语言原始PNG及UI文本；字形/布局与数值应逐类核对，不能用本地化键存在替代看图。 |
| TOOL-CACHED-POPUP | GameObject.Find找到缓存弹窗的外层Root，不代表弹窗正在前台显示；本轮空的GameEnd外壳误使自动观察器提前停止。 | 操作前核对PopupManager当前弹窗、有效子内容及实际截图；重复观察器有时限并记录停止原因，不把事件投递或对象存在当成玩家流程完成。 |
| RUN-LEVEL-SOURCE | CActDragonBattleLevel新表已实际加载，但MActivityRoguelikeTowerMgr.GetDragonRoguelikeLevelCfg直接选择CActivityDragonRoguelikeLevel，再经旧桥接；30关仍旧LevelType1/蛇数据，新表30为Type2，11/25纯兵数据未进入实际关卡。 | S-01 level-config-selection-proof.json、actual-runtime-activity-level-configs.json、loaded-phase4-battle-source.json及冻结源码。区分“新表已加载”和“玩法已消费”；旧桥接ContentID=0是属性约定，不能单凭0判断导入失败。 |
| RUN-PROJECTILE-HIT-LEDGER | 只读真实ECS Phase4SwarmHitComponent与RingHitComponent，记录实体键、目标键、Leg和LastHitAt，可核对实际EmitHit前的去重门槛。 | S-01 projectile-hit-ledger-analysis.json：704个游走弹目标对、546次重复记录，最小间隔约1.033秒，无同Leg更新；16环波36目标对无重复。仅当前实际蛇场景，不外推未激活小兵。 |
| RUN-RING-HOLLOW | 详情文档要求伤害跟随径向波前，各环实体对同目标最多一次；主环、追加环、回流环分别计算。 | S-01 ring-collision-geometry-analysis.json、ring-hollow-negative-analysis.json：54次强候选均命中，57次新命中均有相交位置区间，360次空心内部负向检查无意外命中。须同时采样上一/当前半径、目标位置及碰撞半径，不能只用静态圆环截图推断伤害错误。 |
| RUN-BEAM-MAPPING | 需求及美术详情以多束/多目标为核心；本轮实际基础beamCount仍1，正常BeamSplit与SplitCount词条实现的是分裂弹。 | S-01 english-normal-beam-multiplicity-analysis.json。记录核心多束缺口；K1最终强化名/星级映射未定时单列信息阻塞，不能错误归因为“分裂弹词条承诺多束却未生效”。 |
| RUN-REWARD-FAILURE | 正常有限关自然胜利可建立真实领奖资格；用受控非法索引发真实业务请求验证拒绝，再正常UI重试和重复已领请求。 | S-01两次6关自然End ACK0；受控奖励ACK20后资格/红点/资产不变，正常重试ACK0增币150，重复ACK247161不再发奖。UI显示errCode裸键另记P18。异步资产Ntf稍后到达，不能以ACK后立即值误判漏奖；奖励过期仍须独立到期夹具。 |
| TOOL-BUTTON-DISPATCH | 对象上有Unity Button不保证TFW监听器接在onClick；奖励BoxClose本轮需pointerClickHandler才能触发正常请求。 | 事件返回true后还须检查前台页面、实际ACK及资产/红点；本轮claim-six-box-pointer.cs.txt为身份绑定私有副本，不作为已参数化共享模板。 |
| RUN-CORRECTED-OBSERVATIONS | 英俄主界面战力压叠仅切页瞬间出现，稳定帧正常；30关后续技能页已正常注册且无新的MissingReferenceException。 | 不把稳定帧已恢复的瞬态报告为持续溢出；不因观察器超时或同名弹窗再次出现就断言第二次软锁。排行榜、复活按钮、结算及Arabic数字问题按各自实图保留。 |
| RUN-CLEANUP | 停止Play后再恢复隔离的原角色存档，逐文件校验SHA256、大小与原时间戳；恢复原语言和GameView预设列表，保留未知工作区变化。 | S-01原5份已恢复、中文及原屏幕已回读，临时UniTask依赖路径修复和Library备份保留。Git状态可包含大量无实际diff的刷新标记，应同时保存实际内容差异；并行工作导致配置分支变化时不切回覆盖，继续引用冻结正式表。 |

## 运行与界面覆盖

本轮用例包括三种弹道、盾计次、3/1调度、预算与去重、双源宝箱、复活读档、旧期次、生命周期副作用、英/俄/阿、ESC与Unity屏幕尺寸。首轮已结束，14通过、25失败、46阻塞；通过与失败数量是用例数，不是唯一缺陷数。有限关自然胜利、失败复活、读档、正常消耗与故障领奖、真实命中去重/空心检查、暂停、三语和原生ESC均有证据。实际新表/实例接入失败使小兵、盾和混合无尽的深层断言无法验证；历史格式、低版本、独立到期/跨期和正式配置切换夹具缺口仍开放。未结束当前活动或修改配置强造通过。真机为用户本轮指定范围外；身份绑定的操作副本只留S-01，尚无参数化且重跑验证的共享脚本。

## 首轮后用户决定（2026-11-03）

S-01的decision-confirmations.json已逐项确认18/18。决定不等于修复、部署核实或运行通过，首轮冻结计划、状态和已发布机器报告均保留；原文未回写和回读前，documentBaseline仍为needs_review。

- 版本选择为开发分支配置与dev服务端，用户说明本功能无需服务器修改；重部署后的实际提交须在补验前读取，不能沿用首轮部署SHA。
- 四期以新战斗表及正常生效的小兵/盾/混合无尽为标准，新部署仍异常时按接入缺陷处理。多束、多目标需求保留，分裂弹不能替代多束射线；水环以重新核实的正式配置源为准，不把首轮数值固定为未来标准。
- 重复全选、技能页关闭软锁、技能CD误查表、Unity跨角色存档、持续三语显示和错误提示裸键按缺陷处理。崩溃单独排查，不假定与查表错误有因果关系。
- 活动阵容独立保存，不修改SLG出征阵容，也不弹SLG同步提示；这是用户本轮确认的设计要求。
- 选卡ESC沿用历史行为，不新增放弃确认弹窗。历史基线与目标的UITowerDefenseSlotMachine.cs、BasePopup.cs全文一致，支持沿用判断；没有运行历史版本，不能声称历史实测已通过。P13持续显示问题独立保留。
- 洋红背景本轮暂不处理，下一轮观察是否复现；不将暂缓写成已修复或通过。低分持久化、IsRunning语义及无尽错误恢复仍按已确认条件补验后定性。

私有反馈来源、账号、目标服、环境权限、清理与恢复状态均读取S-01，不写入共享Skill。
