# 雷达怪物击杀计数优化：只读探针使用说明

归属：`k1-radar-monster-first-kill`；入口：[功能档案](../experience.md)。整理日期 2026-10-21；历史实际执行日期 2026-10-10。此轮仅整理文件，未连接 Unity、未编译或执行任何模板、未读取 K1 正式仓库。

这些 `.cs.txt` 是 Unity MCP `execute_code` 的一次性 C# 代码片段，不能当独立程序运行。使用者先读本说明，复制所需模板到本轮 `FunctionPreview/.tmp/<run-id>/`，绑定本轮参数并确认实际身份、测试环境与许可范围后，再交给当前宿主执行；不自动启动、不批量派发。模板保存与历史执行、当前编译、当前执行、业务验收是不同层级。

## 唯一维护源与哈希

原始来源均为 `FunctionPreview/.tmp/nk9973-runtime/<原文件>`，原始回执均为 `FunctionPreview/reports/nk9973-runtime-20261010/evidence/`。这些来源文件不随 Skill 分发。源文件 SHA256 是 2026-10-21 读取时的原文件字节哈希；当前模板 SHA256 标识存档字节，不冒充历史记录当时未保存的文件哈希。

| scriptId | 唯一源文件 | 原文件 | 当前模板 SHA256 |
|---|---|---|---|
| RM-S01 | [radar-account.cs.txt](radar-account.cs.txt) | `account.cs` | `52616B63AF154EE01BD16C4989D04093C827DD752466B59D0FC7359ADD1886EC` |
| RM-S02 | [radar-full-state.cs.txt](radar-full-state.cs.txt) | `full-state.cs` | `ADD3F832F175AE0956D94EF6846E3B80CDB022B59543EA3E5BC25AA666909A95` |
| RM-S03 | [radar-lineup-state.cs.txt](radar-lineup-state.cs.txt) | `lineup-state.cs` | `DAEB11353F0096740B33D40DCEF795CA799CF6CA72C0E840B52D9780364FE1B6` |
| RM-S04 | [radar-map-state.cs.txt](radar-map-state.cs.txt) | `map-state.cs` | `F1159E899BA008A2E897FC0077F09919016FE1A41549F8B69F538DB5A19BE3B3` |
| RM-S05 | [radar-data.cs.txt](radar-data.cs.txt) | `radar-data.cs` | `597330128275378E3791800CBFEC43356744E78AD275FA79902E7EBC94A88505` |
| RM-S06 | [radar-ui.cs.txt](radar-ui.cs.txt) | `radar-ui.cs` | `4C1CFFB550111C7388D87876E63466C4788C76F4C04C5C649A7C6A5AD1B5A099` |
| RM-S07 | [radar-dispatch-state.cs.txt](radar-dispatch-state.cs.txt) | `dispatch-state.cs` | `630165C47B11211CC4CEA5DC096CBE5799DB1CC62B7C907E5130430F3D8EE6AE` |

| scriptId | 原文件 SHA256 | 本次变更范围 |
|---|---|---|
| RM-S01 | `52616B63AF154EE01BD16C4989D04093C827DD752466B59D0FC7359ADD1886EC` | 字节不变，仅归档命名 |
| RM-S02 | `6B5887E3956CD8C9ECD671040B29A5C1E19A036FC74FECF58C0AB45638DEF63E` | 仅把固定 UID/SID 数字替换为两个占位符 |
| RM-S03 | `68C4A60CF7B9A74125D8AA30A0C68CC2A4FBB3216CD5987F518BC7A811DEAC64` | 同上 |
| RM-S04 | `2F20A63F337EAE645F138E941B865591B5AFCF90307837B170425BB64661D1EE` | 同上 |
| RM-S05 | `920A4600C68EAB8DD5A1B5922D910E1B404558BA1977DFC6DCAE42003C3AFFA8` | 同上；归属过滤使用同一 `__PLAYER_ID__` |
| RM-S06 | `4C1CFFB550111C7388D87876E63466C4788C76F4C04C5C649A7C6A5AD1B5A099` | 字节不变，仅归档扩展名 |
| RM-S07 | `630165C47B11211CC4CEA5DC096CBE5799DB1CC62B7C907E5130430F3D8EE6AE` | 字节不变，仅归档命名 |

未新增保护、协议、状态修改或其他执行逻辑。RM-S02～05 参数化后未编译或实测，须在本轮版本下重新复核。RM-S01/06/07 虽与现存原文件字节一致，历史只证明当时版本的读取行为，当前兼容性仍待确认。以后改动模板，应同步更新本表哈希、变更原因、回执和验证状态。

## 宿主、依赖与开始状态

历史宿主为 Unity Editor 的 Unity MCP `execute_code`（`action=execute`），回执编译器 `roslyn`。执行的是代码片段，不是 `.cs` 编译工程。历史客户端为 `dev_NK-9973` / `727614dfb50457b4040f8ae3ed4e1ddabe2661e3`；精确 Unity 编辑器版本、.NET 版本和程序集 ModuleVersionId 未记录，不能宣称与当前环境匹配。服务端和配置的历史身份边界见 [功能档案](../experience.md)。

所有模板开始前须在本轮批准的测试环境中进入 Play 并完成登录，读取实际玩家身份并确认当前 Unity 实例与项目。只查 UI 的模板没有 Play/账号守卫；RM-S04 只比对 UID/SID；RM-S03/05 没有 Play 守卫；RM-S02 不拒绝 `IsGoldEnv=true`，仅返回该字段。这些限制不是整理时新增的保护，必须由操作者先检查。不能把 Inspector 的下一次快捷登录设置当作实际身份，也不能以历史参数替代当前授权。

| scriptId | 具体依赖 / 使用前复核 |
|---|---|
| RM-S01 | `UnityEditor.EditorApplication`、`Logic.LoginMgrNew`、`Logic.LPlayer`、`Logic.CollectAtlasDataMgr`、`Cfg.C.CD2NpcTroopClass`、`Game.Config.MetaConfig`；`GetKillOrderData(id,false)`、`GetFirstKillLevel`、`IsFirstKillTaken`、`IsFirstKillEnabled`、`GetFirstKillMaxLevel` 的语义 |
| RM-S02 | 上述玩家/图鉴/怪物配置类型，另依赖 `Logic.PlayerAssetsMgr`、`K1D2Config`、`Game.Data.GameData.I.LineUpData`、`Logic.LSwitchMgr` 和 `Config.SwitchConfig.AtlasDispatchTroop`。四类怪 cfg 缺失时可能报空引用，不能强行跳过配置检查 |
| RM-S03 | `Game.Data.GameData.I.LineUpData` 的 `lockedList`、`GetLineUpDataByIndex`、`GetNewLineupStateInfo`、`IsLineupIdleForMarch`、`CanChangeLineUpState`、`GetIdleMarchLineUpData`；`cspb.LineupState`、`Config.SwitchConfig.NewTroopState` |
| RM-S04 | `Logic.LPlayer.GetMainCityScene`、`Logic.LCrossServer.CurrSceneType`、`Logic.WMapUtil`、`Logic.LMapEntityManager.GetEntitiesInView`；当前地图/跨服状态已初始化 |
| RM-S05 | `CollectAtlasDataMgr.tasks`、`Cfg.C.CEnergyAtlasMission.I`、`Cfg.C.CD2Search.I`、`LMapEntityManager.GetEntitiesInView`、`NpcTroop.exploreAtlasExt.callerId`；任务配置/搜索配置须存在，未增加 null 容错 |
| RM-S06 | `UnityEngine.Object.FindObjectsOfType<MonoBehaviour>`、`UnityEngine.UI.Text`/`Button`、`EventTriggerListener`；仅按活跃对象路径中的 Atlas/Radar/SearchMonster/CollectDebris 筛选 |
| RM-S07 | RM-S06 的 UI 类型、`DeepUI.SceneManager1.I.FindScene(typeof(UI.UIMain2))`、反射私有字段 `m_IsDispatchingTroop/m_TargetId/m_MarchAct/selectedLineUpIndex`；路径筛选 LineUp/Operation/Dispatch/GM，可能包含 GM 面板的可见文字 |

接口或字段变化时先核对当前代码和配置，不只替换版本标识继续执行。默认不把这些模板用作完整配置检查、服务端权威状态证明或截图替代。

## 全部必填参数与固定业务范围

| 占位参数 | 类型 / 单位 | 使用模板 | 取值与替换要求 |
|---|---|---|---|
| `__PLAYER_ID__` | 数字字面量，按当前 C# PlayerID 字段兼容类型填写；无单位 | RM-S02/03/04/05 | 本轮已核验并获准的实际玩家。RM-S05 出现两次，身份检查和 callerId 过滤必须一致；不要加引号 |
| `__SERVER_ID__` | 数字字面量；无单位 | RM-S02/03/04/05 | 本轮实际 `LPlayer.ServerId`（本服身份），不能拿当前战场/跨服场景 ID 替换；不要加引号 |

RM-S01/06/07 没有模板参数。所有模板没有命令行参数、环境变量或路径参数；不读外部文件，不需要凭证。执行前确认工作副本里没有任何 `__...__` 标记；不把绑定身份后的工作副本写回本目录。

以下是固定业务选择，不是待替换身份参数；其兼容性仍须本轮核对，改变则形成新的未验证模板：

- RM-S01/02 的四类怪 ID 为 `13330001`～`13330004`；RM-S01 仅遍历首杀 1～10 位，RM-S02 仅遍历 1～50 位，不能据此宣称更高等级完整覆盖。
- RM-S02 仅采样资产 `3320046/3320041/20010000/3320057/21110017`、货币 `11151001` 与行动力；不是完整背包快照，也不覆盖全部 GM 恢复奖励。`uiFields` 是历史保留的空字典，不代表读取了派遣字段。
- RM-S05 遍历当前任务和视野内归属本人的含 `exploreAtlasExt` NPC，并未按普通/精英分类；使用 `NpcType`、实际配置与本轮规则判定对象。空列表可能只是目标不在视野或还未下发，不能单凭它断言刷怪失败。
- RM-S06/07 的实例 ID 与 UI 路径随运行改变；不要保存后跨会话复用。活跃对象和文字输出不证明可交互、最终视觉状态或完整业务链路。

## 正常完成、输出与异常处理

片段本身均不写磁盘、不注册回调、不安装后台轮询、不主动发协议或 GM、不更改队列/任务/首杀状态、不消耗资产。输出由宿主返回；调用者在本轮 `.tmp`/报告保存工具回执及必要证据，可能含身份、资产、NPC 和队列数据，应留在本轮来源目录，不能复制到共享 Skill。当前版本若 getter 实现变化，重新核对只读性。

| scriptId | 正常完成信号 / 输出 | 早退或不完整结果的含义 |
|---|---|---|
| RM-S01 | 宿主 success=true 且返回 `uid/server/city/threshold/configVariant/loggedIn/atlas/counters` 对象；核对真实身份 | `NOT_PLAYING` / `NOT_LOGGED_IN` 是成功执行了早退，不能算采样完成；只返回 1～10 位 |
| RM-S02 | 返回身份、四类 counters、energy/maxEnergy、coin/指定 assets、atlas、lineups、atlasDispatch；同一场景前后对照 | `ABORT_IDENTITY` 表示前置或身份不符；资产不是全量，不能据此证明完整背包恢复 |
| RM-S03 | 返回 newTroopState、idleId、逐队列新旧状态和 idle/canChange | `ABORT_IDENTITY` 早退；客户端 idle=true 不能取代本服/战场一致性或真实发兵结果 |
| RM-S04 | 返回身份、cityScene/currentScene/awayFromHome/homeScene/entityCount | `ABORT_WRONG_ACCOUNT` 早退；只证明当前读取场景，不能证明目标可达或战斗成功 |
| RM-S05 | 返回 configs（实际任务/Exp/EnergyCost/Reward/searchType）与 npcs | `ABORT_WRONG_ACCOUNT` 早退；空 npcs 只是该时刻视野筛选结果。核对 owner/type/level，不保存旧实体 ID 作为新目标 |
| RM-S06 | 返回匹配的活跃 UI 列表，每项 id/type/path/text | 空列表或字段缺少只是查找结果；配合当前画面与正常入口，不按旧坐标/实例 ID 点击 |
| RM-S07 | 返回 fields、匹配 UI rows 和 timeScale；检查字段是否实际存在 | FindScene/反射未命中时 fields 可能为空或部分缺失；timeScale 仅回读，不改变时间，不表明派遣成功 |

这 7 个片段均为同步一次性采样，没有脚本内部超时、轮询、异步回执或注销函数；宿主单次超时由本轮工具控制，历史材料未记录统一时限，不能声称已有定时保护。调用结束无需清理游戏状态或注销回调；宿主异常/超时则保留日志、确认是否返回及当前 Unity 连接状态，不通过改内存/删实体“修复”读数。UI 的关闭必须按正常 Close 生命周期操作，探针本身不打开或隐藏 UI。工作副本与回执按本轮留存约定处理，清理文件不会回滚任何游戏进度。

## 历史执行证据与验证范围

本次以现存原脚本内容与历史回执 `params.code` 比较，只统一 CRLF/LF 与首尾空白，没有语义模糊匹配；成功回执均报告 Roslyn。以下日期均为 **2026-10-10（+08:00）**，精确时间保留在原 JSON。匹配审计仅保存来源路径、哈希、时间和成功/编译器元数据，位于 `FunctionPreview/.tmp/feature-archive-20261021/nk9973/archive-audit.json`，未复制账号快照。

| scriptId | 对应历史回执 | 实际证明与不证明 |
|---|---|---|
| RM-S01 | `013-authorized-account.json`；`010-account-after-restart.json` 仅返回字符串 | 013 在已登录状态读取身份/阈值/任务/计数；010 的宿主 success 不等于状态读取完成。无当前版本执行证据 |
| RM-S02 | `030-pre-gm-state.json`、`037-current-state.json`、`042-firstkill-cleared.json`、`050-before-batch.json`、`053-after-batch.json`、`058-after-claim206.json`、`063-reopen-state.json`、`065-restored-state.json`、`067-restoration-verified.json` | 历史可读这些状态；065 是恢复处理中快照，067 才与基线对照。参数化存档未重编译/重跑；读取成功不表示真实战斗通过 |
| RM-S03 | `039-lineup-new-state.json` | 历史读到新部队开关与客户端空闲判断，随后服务器仍拒绝；参数化存档待复核 |
| RM-S04 | `023-current-map-context.json` | 历史读取地图/跨服上下文；参数化存档待复核 |
| RM-S05 | `019-radar-config-and-npcs.json`、`020-spawned-radar-npc.json`、`025-radar-after-relocation.json` | 历史任务配置与视野目标数据，025 支持迁城后目标观察；参数化存档待复核，未覆盖全部生成分支 |
| RM-S06 | `016-map-entry-paths.json`、`018-radar-ui-state.json`、`044-monster-popup.json`、`054-completed-radar-ui.json` | 历史匹配活跃 UI 元素，不是截图/视觉通过证据，也不等于触摸命中 |
| RM-S07 | `033-dispatch-state.json`、`038-after-retry.json`、`040-dispatch-after-attack.json`、`046-departure-f0.json` | 历史读到派遣字段与 UI，不能证明地图实体状态正确或出征成功 |

本批次没有独立隔离模拟或伪造状态验收；GM 前置、只读采样、正常 UI 请求和真实业务结果在 [功能档案](../experience.md) 分开。历史总状态仍为通过 1 / 部分 3 / 阻塞 20，不能以这些探针的执行成功提高业务通过数。

## 未复制的历史脚本

| 历史文件 | 处理理由及保留的证据 |
|---|---|
| `gm-clear-firstkill.cs` | 会清空共享首杀组；有 041 发送与 042 回读，但依赖特定基线、身份和恢复方案。本次不复制执行模板；其历史用途仅为 F=0 的负向前置 |
| `gm-restore-firstkill.cs` | 064 发送、067 进度/位图恢复，068 另有再次发奖流水；恢复并非资产回滚，不能安全泛化为清理脚本。只在档案记录不可逆留存边界，不自动执行、不提供通用复原承诺 |
| `gm-info.cs` | 是历史只读 GM 请求（032），但仍显式发送 GM；已有内存读取探针，未复制 |
| `login-state.cs` | 读取快捷登录配置，易与实际登录身份混淆；使用 RM-S01 核验实时身份 |
| `read_config.py` | 写入固定旧报告路径，读取固定正式仓库，且只抽样 EnergyAtlas/NpcTroopPower；未复制或运行。未来按当前 K1 配置 Skill 获取正式表与实际任务配置 |

没有复制网络封装、报告生成器、工具清单、恢复场景备份或绑定身份的历史执行副本。
