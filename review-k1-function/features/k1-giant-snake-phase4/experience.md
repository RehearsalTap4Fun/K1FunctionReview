# 巨蛇大作战4期：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-giant-snake-phase4 |
| 别名 | 肉鸽塔防4期、巨蛇4期、Phase4Minion、混合无尽 |
| 关联需求 / 分支 | NK-10652、NK-10657 / dev_NK-10652 |
| 更新时间 | 2026-11-12，Asia/Shanghai |
| 最近实际验证 | S-05（2026-11-06～11-09，X15移植后：client 7f1b8308/config de1bdd70/server 2605@e4fe5ba3，macOS Unity）：按用户决定“聚焦移植与反馈”跑108项中的56项：47通过、8失败（开局被拒无提示、服务端全选不去重、寒霜未接入、混合关出蛇波序、复刻音效基础形态回退旧音、英/俄卡名压视频按钮、俄41关标题仍压通行证、阿语Flame Ray漏翻）、1执行遗漏（外围结算）、52用户排除；生命周期TC-85/86/88/89/90首次实测通过。11-09开发另推e01180b2/4eca851c/5c9224bd与config d5fc0859并自测改反馈行26/27/28为已通过，尚未经AI复验。S-04（2026-11-04，client 4177b094/config 40aed93/server 2605@ba9bb524，macOS Unity）反馈表定向复验9项：5通过（全选客户端锁、P18可读提示、基础多束、多重射线四语文案〔按用户“Unity显示即可”改判〕、ESC/结算被拒显示）、4失败（服务端全选不去重、英/阿通行证重复词与英文退出文案仍在翻译母表、俄语41关标题压住i按钮）；其余81项为本轮范围外。S-02（2026-11-03，同版本21cf159/9f4436e，macOS Unity）90项：19通过、14失败、37阻塞、14执行遗漏、6用户排除（生命周期）；小兵/盾/混合无尽仍未生效，根因已定位为新关卡表未接入+实例白名单。S-01首轮85项：14通过、25失败、46阻塞；18条事项待统一决策。不能称这些战斗类型已通过。 |

## 再次验收先看

先读取本轮私有台账中的 checkpoint、授权、计划与 next 队列，不重复询问已确认范围。历史实例、GM许可与部署不是下一轮授权。正式Excel、客户端加载值和服务器部署值分别核验；静态匹配不代表业务通过。

## 预检后文档确认标记（documentBaseline）

| 字段 | 内容 |
|---|---|
| status | precheck_confirmed |
| source | https://alidocs.dingtalk.com/i/nodes/7NkDwLng8ZMa3Y5aTpPpp724JKMEvZBY |
| confirmedVersion / confirmedAt | revision 33；Markdown正文SHA256 4ec8b81f55704f5a24ef04ec76a1c683450ae7dc0170e2df9f254340c01094df；2026-11-06，Asia/Shanghai |
| currentVersion | 同confirmedVersion（S-05运行验收以该版为基线，变更记录1.1） |
| checkedAt | 2026-11-06（S-05预检写入后回读）；运行阶段沿用，未再改原文 |
| evidence | S-05预检FunctionPreview/.tmp/k1-nk10652-20261106-precheck（alignment.md、handoff.json、doc-after.md、result.json）与reports/20261106-100829-4-nk-10652-nk-10657-x15-53e10ef0 |
| reason / nextAction | 用户逐项确认ALN-01～09均为“需求已调整”（逐关生命、淤泥护层、三弹道X15形态、小兵血量、7种刷新、混合关出蛇波序、复刻音效与技能视频），原文与变更记录已更新并回读。之后若纳入新提交（如11-09的e01180b2）只对齐受影响规则。淤泥计次数字显示（a64da10）不在1.1正文内，待用户确认是否属需求。 |

## 来源与版本

| 来源ID | 批次与定位 | 层级与可访问性 |
|---|---|---|
| S-01 | K1FunctionReview/.tmp/k1-nk10652-20261102-unity；客户端21cf159a3edf48da49716ede0ccb154ab84c56f5、正式配置9f4436eb149816db6dbf4cde5c9260ac09fd3c78 | 本机原始证据，不随Skill分发；10份工作簿经Git LFS OID/大小校验，85项用例已编排，首局已实际执行但失败。S-02所在机器上不可访问。 |
| S-02 | FunctionPreview/.tmp/k1-nk10652-20261103-unity（plan-r3/state-r3）与reports/k1-nk10652-20261103-unity-r3；client 21cf159、config 9f4436e、server dev@e116bce；测试服为线上同SID备份导入后本人重建；macOS Unity 2022.3.62f2c1 | 本机原始证据，不随Skill分发；90项用例按同版文档重建，Unity路径实测，真机范围外；生命周期6项经用户决定本轮排除。 |
| S-04 | FunctionPreview/.tmp/k1-nk10652-20261104-recheck（plan/state）与reports/k1-nk10652-20261104-recheck；client dev_NK-10652@4177b094、config 40aed93（客户端产物为bd4b2c74 jenkins导入，本轮未重跑转换）、server沿用remote-jiangzhenyu-gs-2605（dev@ba9bb524，最新dev 1deeaf93仅KVK改动）；S-03批次为k1-nk10652-20261103-recheck | 本机原始证据，不随Skill分发；Unity路径，真机范围外；反馈表待验收/未通过项定向复验。 |
| S-05 | FunctionPreview/.tmp/k1-nk10652-20261106-precheck（静态，冻结client 0f784de7/config a182bac3/server dev e4fe5ba3）与.tmp/k1-nk10652-20261106-runtime（plan/state，运行client 7f1b8308、config de1bdd70、server 2605@e4fe5ba3 备份线上2605重建；11-09实例回收后同授权重建，新匿名角色、GM强开新期）；reports/k1-nk10652-20261106-runtime | 本机原始证据，不随Skill分发；只走Unity路径，真机为范围外；51项老用例与TC-22按用户决定排除。 |
| S-07 | FunctionReview/.tmp/k1-nk10652-20261111-endless（evidence/endless.log、e1/e2/e4-mon/net/bot、截图）与reports/k1-nk10652-20261111-endless/summary.html；client dev_NK-10652@96a62eb8、config 27d4adc583、server dev@343e9994+config b3cf57c4（2605未重部署），macOS Unity 2022.3.62f2c1 | 本机原始证据，不随Skill分发；第41关无尽玩家体验（非完整验收），4局+1次复现，bot自动瞄准选卡。 |
| S-07（6c248026） | FunctionPreview/.tmp/k1-nk10652-20261110-2650-from27 与 reports/k1-nk10652-20261111-2650-player27-to-endless；client 6c248026d4e8、server dev@343e9994b985、config dev_NK-10652@e09bec633 | 本机原始证据，不随Skill分发；第27至40关及满星无尽体验，另含7笔Editor模拟购买。 |
| S-08 | FunctionReview/.tmp/k1-v601-20261111/evidence/nk10652（report.md、r1/r2-net、server-2605-verify.txt、shots/nk10652）；601版本日第20行定向复验；client dev@f3770958（含7f2104e8/066ac313/e466e364）、server 2605 dev@343e9994+config dev@7fdd86cb，macOS Unity | 本机原始证据，不随Skill分发；只复验无尽结算/同步/排行，Unity路径 |

## 已核实的定位与待验证项

| entryId | 事实或方法 | 状态与下次动作 |
|---|---|---|
| CFG-LEVELS | ActivityDragonRoguelikeLevel.xlsx的ActDragonBattleLevelCfg为40普通关＋41挑战；布局24底部/16中心，10小兵关包含11/25两纯兵关。 | 2026-11-02静态核对；运行入口、解锁与胜负仍需实测。 |
| CFG-PROJECTILES | DragonRoguelikeSkill.xlsx的ActivityProjectileParams与客户端Phase4Projectiles.json需逐参数比较；当前水环baseHarm/appendBaseHarm为5.2/6.0与6.5/7.5两组。Phase4BeamRuntime.TryLoadSettings读TextAsset，Phase4RingRuntime消费settings.ring。 | 2026-11-02在S-01实际首局只读比较：导入表5.2/6.0，Active运行对象6.5/7.5（ring-runtime-parameters-first-battle.json）；实际命中伤害和正式导出映射仍待验证，禁止手工改生成配置。 S-02复核：参数是DragonRoguelikeSkillCfg的ActivityProjectileParams列（标记c、类型ext），正式值环5.2/6.0；客户端加载的CDragonRoguelikeSkill该列全空，第41关Phase4RingRuntime实测仍6.5/7.5（来自手工Phase4Projectiles.json）。 |
| CFG-INSTANCE-GUARDS | Phase4MinionConfigStore、Phase4ShieldConfigStore、Phase4EndlessConfigStore按TextAsset.activityIDs检查实例。 | 静态核对；新活动开测先读实际实例ID，分别经正式入口验证兵/盾/无尽，预览成功不能替代。 |
| ENV-DEPLOYMENT | 同名服务端分支缺失时，可由真实Jenkins构建参数定位已部署代码与配置；最新dev和当前运行提交可能不同。 | 方法已用于只读核查；以本轮镜像、构建、实际配置交叉确认，不默默回退分支。 |
| TOOL-ASYNC-REFLECTION | EditorDebugMCP v0.1.0的invoke返回Task本体时，序列化器可能读取Task.Result并阻塞编辑器；本轮调用后编辑器无响应，根因尚待进一步验证。 | 避免返回Task本体；必要异步启动后链式读取IsCompleted等非阻塞值。无响应时保留状态并按本轮权限确认恢复，不能把连接注册当作可执行。 |
| RUN-SKILL-CLOSE | UIEnhanceSkill关闭时执行UIEnhanceSkillData.onCloseCallback；当前抽奖回调捕获UITowerDefenseSlotMachine.SetMaskState，必须关注父界面销毁后引用。 | 2026-11-02 S-01首局9%实际出现MissingReferenceException：SetMaskState:437 → OpenEnhanceUnitPopup回调:575 → UIEnhanceSkill.OnCloseStart:164。页面残留且World未Resume；证据skill-close-missing-reference.log、current-skill-page-check.png。后续版本须正常抽卡并关闭技能页复验，不能修回调后冒充原版本通过。 S-02（同版本）：第1关“巨炮炸弹”技能页、第3关抽奖→“游走弹群”技能页均以BtnClose正常关闭，无MissingReferenceException，选卡与进度继续；本轮未复现，复发条件待查。 |
| RUN-CLOSE-EVIDENCE | ExecuteEvents返回true只证明存在事件处理器；BasePopup.Close会先清空关闭回调/出栈，后续异常可能保留可见对象。 | 2026-11-02 S-01实际验证：页面可见但PopupManager.FindPopup返回null，后续点击无效。观察器遇到同页重复须停止并取异常/生命周期证据，不能把重复页面都记成新开箱或持续盲点。 |
| RUN-SNAPSHOT-ISOLATION | SnapshotMgr.ContainsLastSaveData在UNITY_EDITOR等条件下跳过版本/角色匹配，活动存档目录按玩法前缀分隔，未按角色分目录。 | 2026-11-02 S-01只读存档头与实际提示一致；未恢复另一角色战局，不外推正式包。必要隔离时逐文件保留原路径、SHA256、时间戳并核验备份，验收收尾恢复；账号及原件仅在私有台账。 |
| RUN-ENTRY-PREP | 活动HUD入口仍受主线肉鸽进度与引导条件影响；现有setroguelvl玩家GM可构造主线开放前置，actv rtAddCard可添加活动卡，actv rtSetLvl构造活动关卡。 | 2026-11-02 S-01已验证主线开放、三种新卡添加、正常HUD入口及四卡自动补阵后Save/Start ACK成功；rtSetLvl已实测ACK并更新目标关卡，清除StartingInfo和目标及之后奖励；只用于场景准备，跳关不计自然通关。每次绑定本轮授权身份，IsRunning单一标志不足以防止战中GM，必须同时检查IsPlaying及玩法上下文。 S-02补充：GMReq.args为["actv","rtSetLvl",pid,lvl]、["actv","rtAddCard",pid,card,cnt]、["addasset",pid,"item",id,cnt]（可调UIGM.SendGMReq）；rtSetLvl实测把第1关等更早关卡的rogueLvlInfo也清空，跳关后勿再领取早期奖励。 |
| RUN-INSTANCE-GUARDS | 本轮正常进入3、4、11、41后，Minion/Shield/Endless的Active均为空，实际ActivityID不在各TextAsset白名单；三新弹道却按内容正常激活。 | S-01的level03/04/11/41-phase4-runtime.json及实图；不能写成所有四期功能都未启动，也不能把预览实例当成正式实例证据。相关深层断言保留具体依赖。 S-02复核：Minion/Shield/Endless白名单仅[7699453167230075125,7701911271504192944]，导入线上2650的实例7703789915701510489不在其中；三弹道按contentIDs[100010934]判定故生效。第3/11/4/41关开局Active均空。 |
| RUN-GETALL-DEDUP | 全选锁仅禁用单卡，没有完整阻止全选再次提交；同帧正常pointerClickHandler两次均成功ACK，道具按两个梯度扣除，相同三词条各添加两次。 | S-01 russian-double-getall-protocol.jsonl及前后列表，已记录失败；未伪造网络请求。单次刷新/全选和资源不足结果须独立记录，不能被重复确认失败覆盖。 S-02复现：道具10、单次成本3时同帧两次全部获得均ACK0，10→7→4；道具不足时第二条被3816拒绝只是因为扣光。 S-03复验：客户端同帧二次点击被锁，只发1条请求；直接重复发送请求服务端仍两次扣费(10→8→6)。 S-04：客户端同帧双击仍只发1条(10→9)；绕过UI用MessageMgr.Send重放两条SelectAllOptionReq，两条ACK0，9→7→5，服务端仍不去重。 |
| RUN-PROJECTILES | 实测每组20枚游走弹，重叠施放可有40枚总数；环有同圆心追加和回流缩小，暂停时elapsed/radius冻结。 | S-01 three-projectiles-motion-analysis.json、ring-return-geometry-analysis.json；DTO缺少wave身份，不能用几何样本冒充逐目标命中次数或伤害公式验证。 |
| RUN-REVIVE | 正常自然失败后复活ACK成功、扣道具、已存在蛇回退；累计投放与强化保留，未发现HP补高。 | S-01 russian-revive-analysis.json；仅证明本轮蛇的观察范围，不能外推缺失的小兵、3/1调度、新积分、双源箱。 S-02：读档后第41关失败复活，DragonUnitMoveComponent存活326节ID集合不变、T最大值1.00→0.62；第4关复活后血量标签延续未补满。 |
| RUN-HUD-CARD-LOOKUP | GamePlayEnhanceHeroItem.RefreshCdFill以活动卡ID查CDragonHero，实际每帧缺表错误；本轮另发生一次原生崩溃，managed栈含ExLog工作线程调用Unity日志。 | S-01 runtime-native-crash-preface.log与dump；错误与崩溃并存，不声称已证明因果。正常重启后续测，不自动改业务代码。 |
| RUN-LANGUAGE-RESTART | 现有语言流程SetLocalizationLanguage后Main.ReStart；可自动登录原角色，不一定出现选角页。 | S-01英/俄/阿均真实重进；先读实际身份/语言，避免因没出现选角页而重复登录或误判失败。收尾恢复原语言。 S-02：同序列SetLocalizationLanguage+switchLangeuageing+Main.ReStart约50秒自动重登原角色；阿语界面文本为反向的展示形字形，按名称查找需用实际字形。 |
| RUN-RTL-LAYOUT | 阿拉伯语主活动倒计时和战斗伤害飘字出现水平镜像；结算长技能名压叠数值。英/俄/阿排行榜长标签越入横幅，刷新与全选余次共用“刷新次数”文案。 | S-01多语言原始PNG及UI文本；字形/布局与数值应逐类核对，不能用本地化键存在替代看图。 S-02复核：阿语活动倒计时仍水平镜像；新增：英/俄活动主界面“推荐战力”被拳头图标遮挡，俄/阿排行页页签折4~5行越入横幅，英文通行证名“Serpent Kingdom Kingdom Pass”。 S-03复验(client bd4b2c74)：阿语倒计时与伤害跳字已不镜像，结算伤害值移入进度条且三语技能名完整，全选/刷新次数文案已分开；仍未修：英“Serpent Kingdom Kingdom Pass”、俄/阿页签溢出、俄Auto按钮截断、111020617显示原始键。 |
| TOOL-CACHED-POPUP | GameObject.Find找到缓存弹窗的外层Root，不代表弹窗正在前台显示；本轮空的GameEnd外壳误使自动观察器提前停止。 | 操作前核对PopupManager当前弹窗、有效子内容及实际截图；重复观察器有时限并记录停止原因，不把事件投递或对象存在当成玩家流程完成。 |
| RUN-LEVEL-SOURCE | CActDragonBattleLevel新表已实际加载，但MActivityRoguelikeTowerMgr.GetDragonRoguelikeLevelCfg直接选择CActivityDragonRoguelikeLevel，再经旧桥接；30关仍旧LevelType1/蛇数据，新表30为Type2，11/25纯兵数据未进入实际关卡。 | S-01 level-config-selection-proof.json、actual-runtime-activity-level-configs.json、loaded-phase4-battle-source.json及冻结源码。区分“新表已加载”和“玩法已消费”；旧桥接ContentID=0是属性约定，不能单凭0判断导入失败。 S-02定位根因：DragonRoguelikeLevelCfgBridge无新表转换，客户端手写代码与服务端dev@e116bce均无ActDragonBattleLevel引用（仅Jenkins生成配置类），xlsx的ContentID注明“待程序接入”；新表与正式xlsx逐行一致。 |
| RUN-PROJECTILE-HIT-LEDGER | 只读真实ECS Phase4SwarmHitComponent与RingHitComponent，记录实体键、目标键、Leg和LastHitAt，可核对实际EmitHit前的去重门槛。 | S-01 projectile-hit-ledger-analysis.json：704个游走弹目标对、546次重复记录，最小间隔约1.033秒，无同Leg更新；16环波36目标对无重复。仅当前实际蛇场景，不外推未激活小兵。 |
| RUN-RING-HOLLOW | 详情文档要求伤害跟随径向波前，各环实体对同目标最多一次；主环、追加环、回流环分别计算。 | S-01 ring-collision-geometry-analysis.json、ring-hollow-negative-analysis.json：54次强候选均命中，57次新命中均有相交位置区间，360次空心内部负向检查无意外命中。须同时采样上一/当前半径、目标位置及碰撞半径，不能只用静态圆环截图推断伤害错误。 |
| RUN-BEAM-MAPPING | 需求及美术详情以多束/多目标为核心；本轮实际基础beamCount仍1，正常BeamSplit与SplitCount词条实现的是分裂弹。 | S-01 english-normal-beam-multiplicity-analysis.json。记录核心多束缺口；K1最终强化名/星级映射未定时单列信息阻塞，不能错误归因为“分裂弹词条承诺多束却未生效”。 S-02：第41关12次采样每个cast均Slots=1，正式配置baseCount=1；选卡中未出现增加束数强化。 S-04（4177b094，Phase4Projectiles beam.baseCount=2）：第1关无强化Slots#2、命中表现最多10；“多重射线”111020617每选一次+1，选2次后Slots#4，达上限后13轮选卡不再出现。 |
| RUN-REWARD-FAILURE | 正常有限关自然胜利可建立真实领奖资格；用受控非法索引发真实业务请求验证拒绝，再正常UI重试和重复已领请求。 | S-01两次6关自然End ACK0；受控奖励ACK20后资格/红点/资产不变，正常重试ACK0增币150，重复ACK247161不再发奖。UI显示errCode裸键另记P18。异步资产Ntf稍后到达，不能以ACK后立即值误判漏奖；奖励过期仍须独立到期夹具。 S-02复现：第3关受控索引5领取ACK20后三箱仍可领，正常重试ACK0；已领再领247161；失败飘字同时出现“参数错误（20）”与裸键“errCode:ErrCodeWrongParam”。 S-04：第1关自然通关后受控索引999→ACK20，中英俄阿均只1条可读提示“参数错误（20）”；重复领取247161提示“关卡奖励已领取”、无AssetNtf；点任一宝箱一次领取全部可领索引[0,1,2]。 |
| TOOL-BUTTON-DISPATCH | 对象上有Unity Button不保证TFW监听器接在onClick；奖励BoxClose本轮需pointerClickHandler才能触发正常请求。 | 事件返回true后还须检查前台页面、实际ACK及资产/红点；本轮claim-six-box-pointer.cs.txt为身份绑定私有副本，不作为已参数化共享模板。 |
| RUN-CORRECTED-OBSERVATIONS | 英俄主界面战力压叠仅切页瞬间出现，稳定帧正常；30关后续技能页已正常注册且无新的MissingReferenceException。 | 不把稳定帧已恢复的瞬态报告为持续溢出；不因观察器超时或同名弹窗再次出现就断言第二次软锁。排行榜、复活按钮、结算及Arabic数字问题按各自实图保留。 |
| RUN-CLEANUP | 停止Play后再恢复隔离的原角色存档，逐文件校验SHA256、大小与原时间戳；恢复原语言和GameView预设列表，保留未知工作区变化。 | S-01原5份已恢复、中文及原屏幕已回读，临时UniTask依赖路径修复和Library备份保留。Git状态可包含大量无实际diff的刷新标记，应同时保存实际内容差异；并行工作导致配置分支变化时不切回覆盖，继续引用冻结正式表。 S-02：测试前把唯一RT_P0原档移入隔离目录（SHA256/大小/mtime记录），收尾按原值恢复；本轮RT_P1档由游戏结束/“Delete”流程自行清理。 |
| ENV-EDITOR-VERSION-DRIFT | macOS Editor在Play切换后PlayerSettings.bundleVersion内存值会变回1.0.599（磁盘ProjectSettings为1.0.600，未查明写入方）；活动clientInfo.ClientVersion=600时LoginMgrNew.CheckVersionIsValid(600)=false，主城HUD入口消失。m_LocalVersion启动时缓存。 | S-02已验证：每次进Play前在编辑模式设为检出值1.0.600，登录后核对CheckVersionIsValid与HUD入口；不要把入口消失记为功能缺陷。 |
| RUN-START-ACK-NO-ERRCHECK | OnActvRogueTowerStartAck不判断errCode直接EnterRoguelikeTowerSceneAsync，SendRogueTowerStartReq发送前即改CurLvlCfgID；服务端拒绝（如247155）后客户端仍进入战斗并写本地档。CErrorcode缺247155配置。 | S-02已验证（受控未解锁关开局）；进入后用停止Play退出，并把产生的本地档移出，避免下次“继续挑战”恢复无效战斗。 |
| RUN-ESC-KEYBACK | ESC与返回键共用Main.SimulateKeyBack：活动主界面/排行/暂停关闭正常，选卡弹窗不可被关闭；战斗无弹窗时弹全局“确定要离开游戏吗？”；失败复活界面ESC直接回主城且不发EndReq（半退出）。 | S-02已验证（调用处理函数，非原生按键）；修复后用esc-keyback-step模板逐状态复测，原生按键需另行确认。 S-03复验：战斗ESC改为暂停，失败页ESC先发EndReq(Ack0)显示结算、再ESC退出；EndReq被拒时见RUN-RESULT-REJECT-LOCK。 |
| RUN-ENDLESS-POWER-VERIFY | 战力远低于第41关推荐（4K/120K）时进度同步与结束请求均被247172拒绝，屏幕提示“肉鸽塔防无尽关卡战力校验失败”，但客户端结算仍显示“关卡胜利/本次消灭了60节巨蛇身体”；战斗HUD无本局挑战积分。 | S-02已验证；无尽积分/排行用例需先把阵容战力提升到校验线以上。 |
| ENV-BATTLE-BG-MAGENTA | macOS Editor（Build Target StandaloneOSX）下所有肉鸽战斗背景渲染为洋红，每次开局日志有“Load Scene Error RoguelikeTower”（DEBUG，常驻），属环境材质/目标平台问题。 | S-02已观察；背景/特效视觉结论需在对应平台或真机复核，不据此报功能缺陷。 S-04（11/04）第41关仍复现洋红背景，用户此前决定本轮暂不处理、下轮观察。 |
| TOOL-UNITY-MCP-MACOS | MCP for Unity HTTP服务127.0.0.1:8080（Editor启动）；可用mcporter循环调用execute_code做观察器与ECS采样；ECS为自研LEntityManager，用TryGetComponent<T>与SystemAPI.QueryEntities结构体枚举器反射读取。 | S-02已验证；脚本见[scripts/usage.md](scripts/usage.md)。 |
| RUN-RESULT-REJECT-LOCK | 1cf2c053后UITowerDefenseGameEnd.CanLeaveResult()在EndAck非0时只重发EndReq，无提示无放弃；服务端持续拒绝（247172/247154）时点击返回与ESC都无法离开结算页，冷启动“继续”恢复到同一页。 | S-03（复验，client bd4b2c74）已验证；脱困：冷启动Play→进活动点挑战→“未通关关卡是否继续”选取消（删本地快照）。已记反馈行AI-NK10652-R2-ENDLOCK。 S-04（4177b094）：247172拒绝时结算页显示DEFEAT与可读原因，不再显示VICTORY/奖励；再ESC重发仍被拒停留，用户已定ENDLOCK不处理。 |
| RUN-SOFT-RESTART-STALE | 战斗中/卡结算页时经Main.ReStart软重启（切语言），之后“继续”或新开局StartAck=0但不进场景，日志刷DragonHpTextSystem/DragonBoxSystem NullReference。 | S-03已观察，属测试手法副作用；切语言前先正常退出战斗，出现后停止Play冷启动（版本号设1.0.600后重登）。 |
| RUN-CAPTURE-POPUPS | 登录/回主城/开活动会弹UIFirstCharge3dayNew等礼包弹窗遮挡截图；活动选卡底栏（全选/刷新次数）仅CurLvlCfgID≥CfgActivityBottomUnlockLvRow才显示，第1关看不到。 | S-03：截图前关闭名称含FirstCharge/TriggerGift/Gift/Pack的根Canvas下CloseBtn；选卡底栏与多语言次数文案用第41关验证。 |
| RUN-SETTLEMENT-SKILLS | 第3/40关自然失败结算只列“领主”；需在第41关选到四期技能卡后结算才出现新技能伤害列表；弱阵容第41关5分钟不死。 | S-03：选卡约60~90秒后用LogicMgr.SetComponent把GameStateComponent置Defeat（走正常OnTowerDefenseEnd）进入结算，只证明布局；EndReq会因247172被拒并触发RESULT-REJECT-LOCK，需冷启动取消脱困。 |
| RUN-QUIT-DELETE-ALL | 暂停→退出→“Delete”调用SnapshotMgr.DeleteAllSnapshotsAsync()整目录删除，同设备其他角色的活动存档一并删除。 | S-03两次复现（放入另一角色夹具RT_P1_…121459_268.dat后被删）。测试前须把原存档移出隔离；已记反馈行AI-NK10652-R2-SAVEDEL。 |
| TOOL-DAMAGE-POPUP-MESH | 伤害跳字由DamagePopupManager自绘，不是UI Text/TMP，DamageFlyTextNode下找不到文本组件。 | S-03：读DamagePopupManager.I的m_ParentRect.lossyScale与m_Mirrored判断RTL翻转；视觉以战斗截帧为准（41关选卡频繁，先连点清空选卡队列再连续截帧）。 |
| TOOL-FEEDBACK-COLLAB | 多人协作反馈表使用服务端append追加并分配稳定反馈ID，不以旧行号覆盖；后续插图前重读ID和目标单元格，只补本轮新行。原下拉选项、颜色和单／多选规则原样映射至新行。 | S-01 feedback-sync-verification.json：16条新增反馈、12张截图，原3行、原图和验证语义保留。直接MCP未暴露表格写工具时，DWS可调用底层MCP；附件凭证由现有MCP取得并上传，再写入新行。区域读取不返回嵌图、导出未能完成时，仅用浏览器打开单元格图片及图库，逐张核对实际资源路径、加载完成和原始尺寸；不能以写入成功回执替代在线附图核验。 |
| ENV-I18N-GOOGLESHEET | Unity Editor未设K1D2Config.mCfgVersion时，I18NBootStrap.LoadGoogleSheet在启动时拉在线翻译母表并LocalizationMgr.Init覆盖本地Assets/Res/i18n/*.tsv；Jenkins多语言导出（JenkinsBuildConfigI18N_Mac.sh→downtsv_from_googlesheet_dev.sh）用同一母表。 | S-04已验证：客户端en.tsv手改的subtitle_2/Txt_22在Editor运行时仍是母表旧文案，母表已有的111020617卡文案在Editor能显示但客户端tsv无该键。验收多语言须同时核对母表运行值与客户端tsv（打包来源），不能只凭Editor截图判定打包已修复。2026-11-04用户决定：开发环境以Unity显示（母表）为准，tsv缺键可算通过，打包时手动同步；报告中注明来源即可。 |
| RUN-LANG-SWITCH-COLD | 用Main.ReStart软切语言可能卡在LoadingStep.DoAuthLogin 77%；随后冷启动登录提示“玩家在线”。 | S-04：改为LocalizationMgr.SetLocalizationLanguage后停止/重进Play，再按fastlogin模板登录；遇“玩家在线”时仅对本人测试角色临时把K1D2Config.I.FastLoginForce置true，登录后置回false。阿语界面按钮文字为展示形字形，按名称匹配需用实际字形或按对象路径点击。 |
| RUN-DELETE-EXIT | 暂停→退出→Delete离开战斗不发EndReq，服务端仍在局中；下次点挑战弹“当前还有未通关关卡是否继续挑战”，选取消才清掉。 | S-04三次复现；可用作卡结算外的干净退战方式，但Delete会整目录删本地档（见RUN-QUIT-DELETE-ALL），先隔离原档。 |
| RUN-ESC-AFTER-CARD | 选卡刚关闭的同一刻发ESC，可能被关闭中的选卡弹窗吞掉（不暂停也无暂停页）。 | S-04英/俄/阿各见一次；判定ESC行为前确认暂停页实际出现，未出现则在HUD稳定后重试，不据此报缺陷。 |
| TOOL-FEEDBACK-IMAGE-APPEND | dws sheet range update写richText图片要求每个image带resourceUrl，range read只返回resourceId；已有图片的单元格无法在保留原图的前提下追加新图。write-image只用于空单元格；新增行set-dropdown会把原下拉范围扩到该行。 | S-04已验证：已有问题行只更新文字并在报告保留本次截图，新增行用write-image附图；在线打开核验需浏览器，扩展未连接时记“附件待验证”。 |
| RUN-RU-TITLE-OVERLAP | 俄语第41关标题“41. Бесконечное ИСПЫТАНИЕ”把i说明按钮挤到右侧，被通行证图标压住大半；中英文正常。 | S-04新发现（ru-activity-main.png），已新增反馈行AI-NK10652-R3-RU-TITLE。 | S-05复验：i按钮已移到标题左侧可见可点，但标题未缩字仍伸入通行证图标下，仍未通过（行23已更新）。
| RUN-LIFECYCLE-END | `actv timepass` 推进到 endTs 后本期实例从 info1/list 消失、his 保留；服务端 OnEnd 只做 SendRankRewards 与 RecycleCards。系统邮箱两封同名“[巨蛇大作战]活动结束”：排行奖励（ActvRankSectionCfg→VersionRewardBaseCfg）与碎片回收（Cnt×ConstConfig 10135550 [蓝25,紫100,橙400] 钻石）。未领关卡奖励不补发、下一期清空；活动道具50100000/1/2不回收，下一期开启另发初始各+1；`actv newActv 100109541` 只建主活动，BP/排行/商店需各自实例。 | S-05实测（TC-85/86/88/89/90通过）；外围BP/商店结算需在结束前先产生消耗，本轮遗漏（TC-87）。结束时进行中战局同步被247172/11201拒绝且无奖励，但客户端浮出原始“参数错误（11201）”。推进后用 `actv timereset` 复原。 |
| RUN-SERVER-STALL | 11-09 13:23 起服务端不再回该客户端心跳（进程、端口、模块 goroutine 正常，gsgate 无新连接），结算请求挂起显示“挑战结算中”。 | 恢复：停止/重进 Play→fastlogin；“玩家在线”时仅对本人测试角色临时开 FastLoginForce，期间可能先“登录超时/平台认证失败”，稍后重试成功；登录后补发 EndReq，下次挑战“未通关是否继续”选取消。未定位根因，不作缺陷。 |
| RUN-LANG-NEUTRAL-NAV | 切语言后按文字匹配的脚本（“巨蛇大作战”“挑战”“删除”）失效。 | S-05：活动入口用 HUD ImageIcon sprite `UI_Activity_RoguelikeTower_Icon_Noticeboard` 定位（scripts/open-activity-by-icon），挑战用 `KingInfo/BtnStart`，退战确认用 `ButtonGroup/BtnRedM1`，技能详情翻页 `Banner/RightBtn`、视频 `Banner/VideoBtn`、视频关闭限定 `VideoPanel/Title/CloseBtn`。 |
| RUN-LEDGER-SCHEMA | runtime_acceptance 结果须用 `observation` 与 `{kind,path}` 证据，passed 覆盖全部 requiredEvidence，带 lifecycleAssertionId 的 passed 还要逐 observable 填 observedEffects；blocked 项会阻止 check-advance。 | S-05：临时写法（observed/字符串证据）导致 EVIDENCE_SCOPE_MISMATCH/LifecycleError，返工补证；生命周期前需先让前序阶段全部成为通过/失败/排除。 |
| RUN-AUDIO-BINDINGS | a64da10 起 Phase4SkillAudio 绑定改读 DragonRoguelikeSkill 的 SkillSound/SkillHitSound/AudioIce*；运行探针（scripts/phase4-audio-bindings）可读绑定、已播命中、正在播的施放与缺失ID。 | S-05：幼龙基础100010206=24001005、弹群基础100030106=24001001/24001002 为旧音，开发方案与 d64ddbec JSON 应为24000201、24000208/24000209；其余7条为复刻音。已记反馈行AI-NK10652-R5-AUDIO。 |
| RUN-CONTROLLED-CONSTRUCT | 固定逻辑 Tick 下降帧不能构造大步长；同 Tick 击杀+到达无现成入口。 | S-05：越终点用在场单位 walker 受控 Advance(速度,3600s) 后恢复（scripts/phase4-walker-overshoot）；子关切换不回血用 Phase4PlayerLife.TryDamage 受控扣1血再观察 Phase4EndlessInstance 序号；宝箱到终点用 chest-arrival 探针看 DropID 单位消失、生命减、宝箱队列 granted 不变。均在报告注明受控。同 Tick 裁决（TC-22）仍待开发调试入口。 |
| RUN-PLAYER-EXPERIENCE | 正常玩家体验跑法：领主必须跟随目标走位（FormationSlotManager.HandleMovableModeMovement/HandleCenterModeRotation）；阵容不会自动换成高战力卡，需按 TowerDefenseCardData.CombatPower 取前4上阵；战力远超推荐时出现“碾压”(FastPass)可一次跳多关；复活消耗按1/2/4递增。 | S-06（11-10，client 5889968f→3b4cd629，server dev@343e9994）：不走位/不换阵容时第2～10关反复卡关（数据无效）；换阵容后9.17K→31.37K。第27关告别港湾三蛇是主要卡点（89K/推荐64.8K最好47%，改配置后6%～11%）；GM发碎片至245K后27→40一次扫荡。服务端payTotal $241.90（策略内$121.93，脚本误判多买$119.97）。战斗机器人需挂在Unity内（onBeforeRender），外部轮询每次约1.3s；无尽HUD无“关卡进度”文字需单独判断；隐藏的GamePlay画布会残留。 |
| RUN-ENDLESS-SCHEDULE | 第41关运行时 Phase4EndlessRuntime.Config：maxActive 3、maxMinion 1、minionAliveCap 60、launchInterval 6s、74模板（源L1~L40）。纯蛇模板预算固定1000（与7/28/33/70计分单位无关），含小兵模板=10×(蛇单位+小兵)。CanLaunch 被挡的模板改到队尾（blocked.Order=NextPendingOrder++），不丢弃但打乱顺序。 | S-07（11-11，client 96a62eb8）：三局采样 active≤3、含小兵≤1；单局最多推进到第12/74个实例，tpl7（L3，460兵）因tpl0占小兵名额被挪到队尾，之后所有含小兵模板均未出场；minionAliveCap 未触达（同屏最多18只）、循环未触达。scripts/phase4-endless-monitor 的 cfg 模式可导出模板表。 |
| RUN-ENDLESS-REJECT-OPEN | 无尽结算EndReq被247172拒绝后服务端StartingInfo保留：改阵容TeamSaveReq返回247153（飘字，但界面阵容/战力不回滚，开战用服务端旧阵容）；失败页离开后再点挑战弹“继续挑战”，确认会读档回到已失败战局（生命1、积分为最后存档）；若从暂停→退出→确认主动结束，客户端删存档并置IsRunning=false，再点挑战只发StartReq得247153“肉鸽塔防已经开始游戏”，重进活动无效。 | S-07已复现两次；脱困：冷启动Play→fastlogin重登（InfoNtf使IsRunning=true）→点挑战→“继续挑战”选取消（空进度EndReq返回0）。改阵容前先这样关掉旧局并核对TeamSaveAck errCode=0。已记反馈行AI-NK10652-R7-ENDLESSQUITSTUCK（#68）并补充#61。 |
| RUN-ENDLESS-RANK-SYNC | 局内 ActvRogueTowerSyncProgressReq（约每3秒或选卡时）同样走 VerifyEndlessPower：按积分精确查 ActivityDragonPowerVerify(100010934, Value 1~700) 且开局战力≥Power，否则247172并飘字。排行只随被接受的同步更新：排行积分=40×100+maxEndlessProgress×10，上限11,000，与单局真实积分无关。表在Value 46→47处所需战力43,435→34,748非单调。 | S-07：249K只过360、299.95K只过400~500；13分钟12,082分局排行8,000，1分钟1,740分局因早期同步500通过升到9,000。 |
| RUN-ENDLESS-ECON | 活动道具阶梯（ConstConfig）：刷新50100000 [1,1,2,2,3]、全部获得50100001 [1,2,3,4]、复活50100002 [1,2,4,6]，每局分别5/4/4次；GM `addasset pid item id n` 可补。卡碎片150000201/150000301 addasset 后自动转为卡牌cnt，SendActvRogueTowerCardUpStarReq 每次一档（0→5★共1000），满星返回22004，再 SendActvRogueTowerCardSkillUnlockReq(card,0..4) 解锁星级技能。 | S-07实测阶梯与剩余次数显示一致；满星后海潮/弹群单卡79,670，阵容183.5K→299.95K。后期复活收益低：4次复活共+790分（+7%），后三次各+42~112分。UIEnhanceCard 全部获得档位读 RestAllSelectionCnt（活动中实为已用次数，命名误导）。 |
| RUN-ENDLESS-HP-RESULT | fbebaf7e 后四期无尽按 SpawnedDragonBodySegmentCount 计算龙组血量（scripts/phase4-dragon-group-hp）；失败页 ClickTipText 高80、preferredHeight 135、Truncate，第二行“请点击任意位置返回”不可见（scripts/phase4-result-tip-probe）。 | S-07：第1节6,000→第113节1.46M→第510节37.9亿，113→225节≈1.02^112，#63已通过；返回功能可用但提示截断，#65未通过。 |
| RUN-ENDLESS-VERIFY-SCALE | 服务端 VerifyEndlessPower 用上报值精确查 ActivityDragonPowerVerify(100010934)，表只有 Value 1~700，查不到即 247172（日志 `endless power verify cfg miss`，与战力无关）；第4期客户端上报 Phase4EndlessRuntime.Score，ActDragonEndlessTemplateCfg 74 模板每个 score_budget=1000，所以积分一过700必被拒。排行分=4000+最高被接受值×10（上限11,000）同样按≤700设计。 | S-08（11-12，client f3770958）已验证：299,954战力首同步562通过，1027起全部拒绝，阵亡结算2,996分被拒（DEFEAT无积分），排行只记9,620；积分≤700时结算正常（主动退出16分EndAck=0）；ESC可离开被拒结算页；被拒后点挑战→“继续挑战”选取消即关旧局并可再开局。客户端血量成长/积分分摊修复不解决该问题，需前后端统一口径。复验时先看服务端日志 cfg miss 还是 verify fail，区分“表不覆盖”和“战力不足”。 |

## 运行与界面覆盖

本轮用例包括三种弹道、盾计次、3/1调度、预算与去重、双源宝箱、复活读档、旧期次、生命周期副作用、英/俄/阿、ESC与Unity屏幕尺寸。首轮已结束，14通过、25失败、46阻塞；通过与失败数量是用例数，不是唯一缺陷数。有限关自然胜利、失败复活、读档、正常消耗与故障领奖、真实命中去重/空心检查、暂停、三语和原生ESC均有证据。实际新表/实例接入失败使小兵、盾和混合无尽的深层断言无法验证；历史格式、低版本、独立到期/跨期和正式配置切换夹具缺口仍开放。未结束当前活动或修改配置强造通过。真机为用户本轮指定范围外；身份绑定的操作副本只留S-01，尚无参数化且重跑验证的共享脚本。

S-02（2026-11-03，同版本）：Unity路径90项实测，19通过/14失败/37阻塞/14执行遗漏/6用户排除。通过：正常入口、通关解锁、关卡领奖与失败重试/重复领取、刷新与单次全选、复活扣费与后退、读档恢复、选卡暂停冻结、蛇身挂箱与K1选卡、三弹道作为活动卡接入、游走弹20枚持续游走与命中台账去重、技能页关闭无软锁。失败：开局Ack不判错、新关卡表未接入（第3/11/4/41关仍旧数据）、小兵/盾/无尽实例白名单、幼龙单束、环伤害参数与正式配置不一致、全选同帧双扣、ESC半退出与战斗中弹退出游戏、英/俄/阿显示问题。阻塞：依赖小兵/盾/混合无尽/挑战积分的37项及环境不可构造的兼容项；执行遗漏：同帧裁决、低帧越点、环带几何与空心负向、射线跟随/重选、多箱、未处理箱结束等专项采样。生命周期6项因前序阻塞无法通过check-advance，经用户决定本轮排除，待P0修复后在新部署连同前序阻塞项复测。反馈表来源与字段映射记录在S-02私有笔记，不写入共享Skill。

S-04（2026-11-04，client 4177b094，2605@ba9bb524）：开发按上轮反馈修复后的反馈表定向复验，Unity路径9项5通过/4失败，81项范围外（TC-34按用户决定由失败改判通过，#4/P16已通过）。通过：客户端全选防重、领奖错误提示四语可读（P18已通过）、基础2束且强化到4束、ESC暂停/结算被拒显示DEFEAT与原因。失败：服务端全选重放仍双扣（#6）、英/阿通行证重复词与英文退出文案仍在母表（#8，开发只改了en.tsv）、俄语41关标题压住i按钮（新增行）。本轮未跑配置转换（测试服Jenkins无该任务、本机无客户端Jenkins凭证），跑转换会向dev_NK-10652推提交并按母表覆盖en.tsv手改。

S-05（2026-11-06～09，X15移植，client 7f1b8308/config de1bdd70/server 2605@e4fe5ba3）：先远端冻结做静态预检与9项文档对齐，再Unity路径运行56项：47通过/8失败/1执行遗漏/52排除。新通过：逐关生命3、淤泥护层三档与破盾吸收、幼龙1束+焚阵与多束、海潮前向与满潮回环、弹群2枚与熔潮终式20枚、小兵血量显示、Legacy刷波节奏、纯兵关、宝箱到终点、越终点、无尽子关不回血、技能视频、客户端全选防重、生命周期五项。失败：开局被拒无提示、服务端全选重复扣费、寒霜未接入、DragonSpawnWaves未读取、基础形态复刻音回退、英/俄新卡名压视频按钮、俄41关标题压通行证、阿语111020619漏翻。洋红背景仍在，按环境问题处理。

S-07（2026-11-11，client 96a62eb8，第41关无尽体验报告）：旧最强阵容249K 8,829分/5:50；三新0★+神圣之光183.5K 9,042分/8:12（复活2）；三新满星+神圣之光299.95K 12,082分/13:40（复活4，刷新5、全部获得3）。新技能为主力（满星时游走弹群占71%伤害）。所有结算与局内同步（积分>表内阈值）被247172拒绝，排行只记早期同步；结算被拒后旧局不关闭导致阵容保存被拒、可读档回到已失败战局、主动退出后需重登才能开局（新增#68）。#63龙身血量成长通过，#65返回可用但提示截断未通过。调度符合3/1，但被挡的含小兵模板移到74模板循环队尾，实际单局只见tpl0一个含小兵小关（待策划确认）。

S-08（2026-11-12，601版本日第20行定向复验，client dev@f3770958）：7f2104e8/066ac313/e466e364 改了无尽血量成长（Base 300000×seq^2.5，10后×(seq/10)^2）和积分分摊，但服务端校验表只覆盖积分1~700，第4期每模板1000分，同步与结算超过700仍全部247172，排行只记首次同步，仍未通过（反馈行61已追加）。同一299.95K阵容由13分40秒/12,082分降为135秒/2,996分。活动结束结算与#68主动退出路径本轮未重跑。

## 首轮后用户决定（2026-11-03）

S-01的decision-confirmations.json已逐项确认18/18。决定不等于修复、部署核实或运行通过，首轮冻结计划、状态和已发布机器报告均保留；原文未回写和回读前，documentBaseline仍为needs_review。

- 版本选择为开发分支配置与dev服务端，用户说明本功能无需服务器修改；重部署后的实际提交须在补验前读取，不能沿用首轮部署SHA。
- 四期以新战斗表及正常生效的小兵/盾/混合无尽为标准，新部署仍异常时按接入缺陷处理。多束、多目标需求保留，分裂弹不能替代多束射线；水环以重新核实的正式配置源为准，不把首轮数值固定为未来标准。
- 重复全选、技能页关闭软锁、技能CD误查表、Unity跨角色存档、持续三语显示和错误提示裸键按缺陷处理。崩溃单独排查，不假定与查表错误有因果关系。
- 活动阵容独立保存，不修改SLG出征阵容，也不弹SLG同步提示；这是用户本轮确认的设计要求。
- 选卡ESC沿用历史行为，不新增放弃确认弹窗。历史基线与目标的UITowerDefenseSlotMachine.cs、BasePopup.cs全文一致，支持沿用判断；没有运行历史版本，不能声称历史实测已通过。P13持续显示问题独立保留。
- 洋红背景本轮暂不处理，下一轮观察是否复现；不将暂缓写成已修复或通过。低分持久化、IsRunning语义及无尽错误恢复仍按已确认条件补验后定性。

私有反馈来源、账号、目标服、环境权限、清理与恢复状态均读取S-01～S-04私有笔记，不写入共享Skill。

## S-07（6c248026） 玩家体验增量（2026-11-11）

来源 S-07（6c248026）：Unity本轮冻结client 6c248026d4e8、server dev 343e9994b985、config dev_NK-10652 e09bec633；私有回执与原图在 FunctionPreview/.tmp/k1-nk10652-20261110-2650-from27，汇总在 FunctionPreview/reports/k1-nk10652-20261111-2650-player27-to-endless，不随Skill分发。此为第27关起的玩家体验，不能覆盖历史详细用例、其他语言、活动生命周期及真机缺口。没有修改业务代码或正式配置。

| entryId | 状态、结论及适用范围 | 验证与下次操作 |
|---|---|---|
| RUN-ENDLESS-SCORE-VERIFY | 已验证：上述服务端按(ContentID,progress)精确查ActivityDragonPowerVerify；四期Content100010934正式源仅Value1..700，客户端上报挑战积分。满星power492294仍在966分起被247172拒绝，最终11956分未落库，best660；普通返回后正常重登IsRunning=true/IsPlaying=false。 | 2026-11-11 S-07（6c248026）：359对Sync请求/回包、实际容器cfg miss、冻结源码、正式XLSX及最终EndReq/重登互证。此版本不能沿用旧RUN-ENDLESS-POWER-VERIFY“只补战力即可”的建议；开发统一积分/校验语义后复测Sync、End、best与StartingInfo清理。未绕校验、未GM清现场。 |
| RUN-PLAYER-27-40 | 已验证：14关15战，38首次54.76%失败后正常补强重试，40复活4次共13券；全部尝试总全选87券、复活22券。27最初一段沿用AUTO=true后经正常UI关闭，其后false，非全段纯手动对照。 | S-07（6c248026）各关before/胜负/EndAck0/领奖/指标台账。38策略、随机结果与战力均变化，不能把重试改善全归因于加战力；40战斗完成后遗留HUD100%尚有一组残血为待决体验观察。 |
| RUN-FULLSTAR-OPTION-INDEX | 已验证：14卡最高星级来自正式源，两个蓝卡3星、其余12卡5星；102有两条3星词条，全卡共67配置列表项。 | S-07（6c248026）正式表、运行卡状态及正常UI逐项解锁回读；按列表索引处理，不能按星数推算索引。GM补碎片/升星仅为无尽夹具，不计作正常付费养成通过。 |
| RUN-REVIVE-COSTS | 已验证：正式10135548数组为1/2/4/6，第4次6券。 | S-07（6c248026）实际40关四次复活与源表。辅助输入守卫必须读当前复活次数和正式数组；本轮误推8时仅修正守卫并在同一局继续，不能记成第2次挑战或产品故障。 |
| RUN-PAY-EDITOR-BOUNDARY | 已验证：正常UI触发Unity内建Editor模拟购买，7笔到账/限购/正常重登成功；未产生真实CreateOrder，SDK渠道支付仍阻塞。 | S-07（6c248026）七组请求/奖励通知与重登对比。区分内建Editor测试购买和直接GM补养成，不能用二者证明真实SDK渠道支付。 |
| RUN-SHOP-LIMITS | 已验证：蓝自选044与紫自选049正式limit=-1不限购；048中级随机150，050混合随机300，051橙自选50。 | S-07（6c248026）正式表与实际UI。旧“紫自选36/50”推断失效，后续按源表/运行时读值。 |
| RUN-HUD-100-REMAINING | 待决体验观察：40关进度显示100%时，一组仍20166/1325998HP，之后要求复活。 | S-07（6c248026）原HUD及实体采样；推荐未全清前最多显示99%，由策划决定。不能表述成全体敌人已死仍失败，不据此覆盖旧反馈的开发结论。 |

清理已验证：原登录标志、测试购买开关、AUTO及GameView恢复，三份隔离原存档按哈希恢复，自有回调与探针清理，未保存原本已脏场景；并发仓库改动全部保留。协作反馈表元信息可读但范围读取持续6000ms超时/断连，未写任何单元格，在线维护待服务恢复后按最新单元格合并。无新增共享脚本；身份绑定执行副本只保留本地。
