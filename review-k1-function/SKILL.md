---
name: review-k1-function
description: Align K1 requirements and run static prechecks or runtime acceptance, including multilingual UI and screen adaptation checks. Use for version package acceptance and DingTalk progress broadcasts, preparing a personal test environment from an online game or battle server, backing up via Jenkins, obtaining the DingTalk DownKey, deploying independent code/config branches, or continuing partially verified cases.
---

# K1 需求对齐与静态预审、运行验收

## 分享与首次使用

向他人分享、迁移到新机器或首次使用时，先读取 [references/dependencies-and-setup.md](references/dependencies-and-setup.md)，按本次场景说明必需的外部 skill、CLI/MCP、凭证和权限；只核对存在性与可用性，不显示密钥内容。缺少依赖时指出影响的具体阶段及补齐方式，不把所有可选依赖都当成前置，也不把只读连接成功当作具备构建权限。

分享完整 `review-k1-function/` 与仓库内的 `slg-testcase-generator/` 目录及被调用的脚本/资源，提醒接收者分别注册 Skill，并配置自己的账号和本地路径。Jenkins Token、DWS 登录态、Git/SSH 私钥、MCP 连接密钥和运行回执不随 skill 分发；不得让接收者在聊天中粘贴密钥。

## 定位

首次完整预检先完成需求对齐，再生成或校准用例、执行静态预审。接续运行验收先核对分功能经验中的“预检后文档已确认”标记；当前版本一致时直接沿用，变化时只对齐受影响规则。运行验收由用户指定时间节点：功能开发完成时验收或版本日验收；默认覆盖 Unity 与真机包两条路径，用户明确限定客户端路径时按其范围执行，并在结论中注明未测路径不属于本轮结论。现有 `acceptanceMode` 分别记录节点范围，客户端路径另记；共同前置见 [验收节点与客户端路径](references/runtime-client-modes.md)。需求对齐和静态预审两阶段均不限时；运行验收同样以本轮范围和真实证据为完成依据，不按累计耗时收尾。

静态输出必须显著声明：**这是静态预审结果，不代表功能验收通过。** 运行报告独立记录实际部署版本、验证方式、覆盖缺口和留存状态。

不提供完成度百分比，也不自动修复业务代码或修改三端正式配置。允许为需求补齐必要的调用链和跨端证据，不能因时间、采集轮次或调用跳数截断核查。

## 入口路由

- “版本进包内容表验收 / 版本进包项进度播报”：读取 [版本需求进度与钉钉播报](references/acceptance-progress.md)。同一版本日完整需求清单共用台账，先记录开始状态，每项需求形成结论后调用 `python scripts/acceptance_progress.py record` 保存并立即播报标题、结果与总数/已完成/待验收/正在验收/未完成；子用例不计为需求，验收结果与通知送达分别记录。续跑与收尾检查待发送、失败和待核对消息。仅向用户已指定并授权的机器人发送，Webhook 留在私有配置。
- “备份线上服并建测试环境 / 复制战场服 / 指定线上 SID、代码分支、配表分支部署”：直接读取 [references/jenkins-test-environment.md](references/jenkins-test-environment.md) 的整链入口，使用 `scripts/jenkins_environment_workflow.py`。这是独立环境任务，不要求先做策划文档对齐或静态预审。默认本人同 SID；战场服同样先备份，部署 `app=battle`；未指定保留列表则全量恢复，指定列表则按列表保留。沿用明确的备份、导入与重建授权，禁止覆盖他人实例。
- “预检 / 静态预审 / 需求对齐”：执行下述静态流程。仅提供 Jira 单号或分支名，不自动授权部署。
- 活动类功能必须执行 [活动生命周期与补验合同](references/activity-lifecycle.md)：记录开启、进行、结束、结算、回收、关闭清理和下一期；结算按六类独立副作用拆断言，未充分需求、风险和历史补验都进入可校验台账。原文没有写“幂等”也要检查结束发奖防重与失败恢复。
- “提 Bug / 提交 Jira 缺陷”：仅用户明确要求建单时，调用仓库内已注册的 `$jira-bug-creator`，按其 NK 规则整理证据、提交并回读；验收发现问题或维护反馈表不自动创建 Jira 单。
- “运行验收 / 测试 / 继续补验”：继承已确认的需求、操作范围和已有证据，完整读取 [references/runtime-acceptance.md](references/runtime-acceptance.md)。先核对文档确认标记，再按用户指定的验收节点和客户端路径确定范围，为本轮路径生成计划；已有有效交接直接续跑，不重问旧决定。功能开发完成时按文档及反馈表详细验收；版本日按文档规则进行正常玩家体验，不自动套用全量开发用例或反馈复验。节点不能仅凭分支名或日期猜测。
- 每个指定验收节点开测前先运行配置表转换与多语言转换任务，优先使用 `K1_Build_Config_I18N_Mac`；转换成功后按 [设备与测试服隔离](references/device-server-isolation.md) 为本轮每个客户端实例启动专属服务器，确认实际连接目标服后才验收。两条路径使用完全相同的转换输入和产物时可共用本轮转换回执；默认每个客户端实例一独占服务器实例，同轮续跑可复用本轮已启动且仍有效的实例。缺分配或必要部署信息时先查后问，只暂停受影响客户端的部署和游戏操作；继续文档、反馈、计划、版本与工具连接等独立准备。同服例外需用户明确指定，服务器级 GM 统一协调。
- 已有明确验收列表时，开测前先输出有序计划：检查状态和时间依赖、合并可共享准备与操作的项目、保留逐项结果和证据，再按资源隔离情况安排协作者分批并发。具体字段和派发规则见 [运行验收 §3](references/runtime-acceptance.md#3-冻结可执行断言计划)。
- 验收项涉及新增界面或旧界面改动时，两类验收都按 [UI 多语言与屏幕适配规则](references/ui-language-and-screen-adaptation.md) 对受影响界面切换英语、俄语、阿拉伯语，逐语言检查显示并保存截图。多项任务默认按语言集中验证，减少重启切语；每项完成全部必要验证后立即更新文档状态并回读，不等待整批结束。缺少必要语言验证时保留补验/阻塞，不能整项通过；结束恢复原语言。版本日的 Unity 与真机路径同样执行这三语检查，范围限于受影响界面，不自动扩展全部功能或屏幕组合。
- 每次功能任务先按 [经验读写规则](references/feature-experience.md) 查询 [功能索引](features/index.md)，读取对应档案及需要的脚本说明；每阶段结束、交接或中断前自动合并有证据的新经验，并报告回写结果。版本变化先核对适用性，历史验收结论不直接沿用。黄金矿工使用 [独立档案](features/k1-gold-miner/experience.md)。
- 两个验收节点的所选路径均按 [运行验收规则](references/runtime-acceptance.md) 检查相关界面/玩法的返回操作：Unity 按 ESC，真机用设备返回键或模拟返回键，核对弹窗、页面和 HUD 在返回前后的状态，分别留证。
- 重复运行操作先查 [已学习流程](references/learned-runtime-flows.md)：首次学习入口与成功条件，后续复用有时限的状态流程，用回包/权威状态确认；新界面、异常和视觉断言再看图。固定导航可复用，关卡策略与本轮授权不能盲目沿用。
- 反馈表复验必须逐项查看原问题截图及预期/参考图，记录原图与本次实测的对应关系；新增反馈附本次问题截图，并验证在线附件可打开。图片读取为空不代表无图，未查看原图不得认定原问题已复现或已修复；具体记录和附件核验见运行验收规则。
- 两类运行验收先按 [反馈文档准备与维护](references/feedback-document.md) 查找反馈表并检查必需字段。未提供链接先查任务与功能经验，确实找不到才确认“补链接或新建（推荐）”；已有授权直接沿用。字段有则语义映射，缺则在原表补建；没有整表才走新建表分支。逐项验收后维护反馈、回读及核验附件，再进入需求结论播报与归档清理；待同步时保留证据，独立验收继续。
- 同步或整理反馈表时，截图统一追加到对应行的“问题截图”单元格，保留原图并支持多图；验收只保留一个状态字段，必要说明合并到“验收详情”。按 [运行验收规则 §4.2](references/runtime-acceptance.md#42-反馈表字段整理与格式保留) 做最小范围写入，并回读核对原有下拉验证、选项、颜色与适用范围。
- 结果已写入文档并回读、逐图核验后，按 [过程文件归档与清理](references/runtime-artifact-cleanup.md) 自动删除本轮不可复用且无依赖的临时文件；先迁移可迁移的引用，保留未同步、待补验、机器校验依赖的证据及正式台账，不清空整个工作区。
- 运行阶段缺环境：读取 [references/jenkins-test-environment.md](references/jenkins-test-environment.md)，从 Jira 关联、远端分支及 Jenkins 历史分别解析代码和配置来源，在已授权测试服范围内准备并部署。部署成功后验证实际运行状态，再继续原补验队列。不能把本地仓库位于其他分支、Jira 无验收描述或 MCP 返回 `auth required` 直接当作整轮终止理由；分别查目标版本的隔离运行入口、关联文档及连接修复路径，并记录实际尝试。
- 不把“部分验证”当作结束状态。每轮调用 `scripts/runtime_acceptance.py next`，执行可继续动作；推进时间前调用 `check-advance`；最终运行验收报告只能由 `publish` 在收尾检查通过后生成。尚未确定节点或文档基线、无法建立有效计划时，只能交付明确标为“前置检查／待续”的记录，列出已完成、未尝试、真正阻塞及各自下一步，不称为运行验收结论；交付前核对本地报告链接确实存在。

## 功能审核开始前必读

以下前置适用于首次需求对齐和完整静态预检。接续运行验收按运行入口核对已有文档标记与交接，不自动重跑完整静态工作流；版本日验收不要求为本轮重建全量开发用例。单独准备环境使用上方独立入口，环境就绪后不能宣称功能验收通过。

1. 完整读取 `references/requirement-alignment.md`，执行必经的文档对齐、用户确认、原文维护和交接合同；使用 `assets/requirement-alignment.md` 展示增删改清单。
2. 完整读取 `references/quick-precheck.md`，执行输入、远端快照、证据、降级和报告合同。
3. 完整读取 `references/k1-project.md`，使用固定仓库路径、远端来源和文档路由。
4. 使用 `references/k1-review-rules.json` 作为机器可读检查目录；不得凭记忆删减其中命中的规则。

## 默认决策

不要询问可从环境发现的事实，也不要让用户为了审核切换或保持本地分支。

- 普通分支名默认 `source=remote`、`remote=origin`、`baseBranch=dev`；三端默认使用同名 target。
- 每次完整工作流开始时实时联系 `origin`，在 FunctionPreview 隔离缓存中精确 fetch base/target，并立即冻结完整 SHA。对齐、确认、文档维护、用例和预审沿用同一 manifest；交接时不刷新移动分支。纳入新提交必须重新对齐。
- 完整 40 位 SHA 或显式 `source=local` 才走离线/冻结本地对象模式。
- 远端失败绝不回退本地 `refs/remotes/origin/*`、当前 `HEAD` 或当前工作区；只把受影响端降级为 `无法确认`。
- 完成对齐后，依据更新后文档校准已有用例；缺少覆盖时使用仓库内已注册的 `$slg-testcase-generator`，按其 `references/static_acceptance.md` 生成本地 Markdown 用例。覆盖所有需求、主流程、边界和异常，无累计时间或用例数量上限；不使用旧快速模式的限额。QA Skill 的标准在线流程（`testcase-config`、七步写表、预计数量）不属于本静态预审步骤；本步骤仅按该 Skill 的 K1 静态用例规则执行。
- 用户确认并回读核验后的开发文档定义需求。三端实现用于发现差异，不能自行覆盖文档；已有用例也不能覆盖开发文档。
- 配置 target SHA 上的正式 `.xlsx` 是最终状态。生成 JSON/TSV 是次级证据，《配置表结构》等文档仅用于定位。

环境事实先查。文档差异必须逐项有用户决定，可按编号批量回复；未回答不等于同意。需求含义或源文档不明时澄清，远端失败不能让用户猜测实现事实。

## 只读与写入边界

静态阶段正式 K1 仓库只读；运行阶段沿用源代码与正式配置只读边界，另按下述例外操作测试环境：

- Client：`C:/Project/K1Client/k1_client`
- Server：`C:/Project/K1Game/game`
- Config：`C:/Project/K1Dataconfig/dataconfig`

macOS 上 `C:/Project` 对应 `~/Project`（或 `$K1_PROJECT_ROOT`），FunctionPreview 指本仓库根目录，`.ps1` 由 `pwsh` 执行；见 [macOS 安装与首次配置](references/macos-setup.md)。

所有 Git refs/objects、锁、LFS 对象、临时文件和报告只能写入 `C:/Project/FunctionPreview` 的 `.cache`、`.tmp` 或 `reports` 子目录。额外允许按用户逐项确认结果最小更新指定原策划文档及其变更记录；这不授权修改三端仓库、代码或配置。原文档位于正式 K1 仓库内时仍遵守仓库只读边界，明确请求可维护的文档来源。

正式 K1 仓库禁止 `fetch`、`pull`、`checkout`、`switch`、`reset`、`clean`、`stash`、`add`、`commit`、`merge`、`rebase` 和任何 Git LFS 命令。静态阶段也禁止编译、测试、启动、运行验收、导表、配置/代码/资源生成、依赖安装、子模块更新和 Jenkins。

运行阶段及独立环境任务的明确例外：可在已获授权的服务器/账号范围内使用 Unity、正常业务请求、现有 GM、故障模拟和测试部署任务；用 `scripts/jenkins_environment_workflow.py` 执行已授权的线上备份 → 钉钉 DownKey → 本人测试服导入重建 → 运行校验；只部署已有 Key/空服时仍可使用 `scripts/jenkins_test_environment.py`。两者读取项目本地连接配置。探针和隔离测试写入 FunctionPreview，禁止借测试任务修改正式业务源码、清理与本轮无关的用户文件或发布线上热更。清档、导入、改时间依照实际已获授权范围分别记录，不从“允许部署”推导清除数据的权限。Unity 自身产生的资源/缓存变化如实披露，不擅自回滚。

唯一允许的网络 Git 写入命令由 `scripts/prepare-remote-snapshots.ps1` 在 FunctionPreview 远端缓存中执行；唯一允许的 LFS fetch/smudge 由 `scripts/export-git-file.ps1 -MaterializeLfs` 在该缓存中执行。不得手写替代命令绕过脚本边界。

经验维护的文件写入例外：按 [经验读写规则](references/feature-experience.md) 更新本 Skill 的 `features/` 索引与档案，及已走通流程所需的 `features/<featureId>/scripts/` 模板和说明；既有公共执行脚本只引用，不因记录经验而自动改写。原始截图、回执、身份绑定执行副本仍保存在 FunctionPreview 的 `.tmp` / `reports`，不随 Skill 分享。此例外适用于静态与运行阶段的经验归档，不授权静态阶段执行运行脚本，也不改变三端正式仓库只读边界。

运行过程文件的删除例外仅限上述归档与清理规则：本轮自建临时目录内已核验、无依赖的一次性文件可自动清理，正式证据、用户原件和其他任务文件继续保留。

## 完成标准与单次超时

- 对齐和预审均无总时限，`deadlineSeconds=null`。记录实际耗时，持续报告已覆盖内容、未决项和下一步。
- 保留单次远端准备默认 180 秒、单次 LFS 物化默认 120 秒、单条代码定位默认 30 秒与单次 Git 最多 5 秒，防止工具挂起；这些不是工作流或阶段总预算。
- 超时后定位原因，在同一冻结 SHA 上按需补证；真实不可访问或必须运行才能核实的内容记录原因和验收动作。不得因累计耗时而停止补证或强制降级。
- 每项文档需求、相关增删改及跨端依赖都要有处理结果。不得将未知当作已验证，不承诺静态审查能证明运行行为。

## 静态阶段固定顺序

### 1. 创建运行边界并快照

- 创建唯一的 `C:/Project/FunctionPreview/.tmp/<run-id>`。
- 调用 `scripts/snapshot-repository-state.ps1` 记录三端 before digest。
- 记录开始时间；检查 24 小时分析缓存，但不得用缓存跳过本次完整工作流的实时远端解析或文档对齐。
- 读取本功能档案，在本轮 `experience-notes.md` 记录所用档案版本、可复用线索及待复核项；对齐、预审结束或中断时按经验规则回写增量。

### 2. 冻结审核对象

- 对普通分支名，一次调用 `scripts/prepare-remote-snapshots.ps1`；脚本并行准备 Client、Server、Config。
- 只接受脚本 manifest 中的 `source=remote`、`origin`、base/target ref 和完整 SHA。
- 单端 `REMOTE_BRANCH_MISSING`、fetch/认证/过滤失败或超时只影响该端；禁止本地 ref fallback。
- 将 manifest 的缓存仓库路径、`baseSha`、`targetSha`、`baseRef`、`targetRef` 原样传给 collector。

### 3. 必经前置：对齐并维护策划文档

- 调用 `scripts/collect-git-evidence.ps1` 处理三端冻结 SHA；对齐和预审共享 commits、merge-base、changes 和逐端错误，不因单端失败取消成功端。
- 远端模式只从 FunctionPreview 缓存读取 commit/tree/blob，不读取缓存工作树状态，也不重新解析移动 ref。
- 按 `references/requirement-alignment.md` 逐项比对原文档、三端分支累计提交和 target 最终状态，列出新增、删除、修改及待判定项。
- 用户按编号决定「需求已调整」「实现有问题」「证据不足」；只有需求已调整的条目回写原章节并追加变更记录。
- 写入前复读，写入后回读；保存前后文档版本、确认依据、已应用条目和待查项。原文未更新、写入失败或有未确认条目时，前置工作流尚未完成，不能进入后续工作流。
- 用 `scripts/requirement_alignment.py --input <handoff.json>` 校验完成记录。无差异也要保留覆盖说明、同版本回读和空清单，无需空清单确认。

### 4. 生成／更新测试用例，绑定需求与文档版本

- 按更新后的开发文档顺序保留每项需求和定位；删除需求保留对齐清单记录，移除或校准过时用例，不继续作为验收要求。
- 校准已有用例的前置条件、操作和期望，补齐覆盖，建立 requirement ↔ testcase 双向关联；记录 `testcaseDocumentVersion` 等于回读后的文档版本。
- 「实现有问题」「证据不足」通过 `requirementIds` 交给预审逐项核查，不能在文档对齐中消失。
- 活动类在同一 PrecheckResult 建立 `activityLifecycle` 和 `followupObligations`，按 [合同](references/activity-lifecycle.md) 填全阶段、独立断言与来源 ID；每个待补验项绑定具体动作及关闭标准。未进入产品缺陷反馈表的测试覆盖不足仍须独立跟踪。

### 5. 需求驱动的静态预审

- 从 Git diff 和 changed paths/symbols 建立索引，沿需求相关的调用者、被调用者、协议和配置引用追踪，直到能够解释业务闭环或明确证据缺口；记录扩展理由，无固定一跳限制。
- 不做无目标全仓扫描，不能用“未出现在 diff”单独证明缺失；无 diff 的文档需求也检查 target 最终状态。
- 只对需求或直接代码引用命中的 workbook 调用 `scripts/export-git-file.ps1`。
- 远端 `.xlsx` 若为 LFS pointer，必须使用 `-MaterializeLfs -Remote origin -ExpectedLfsPath <exact-path>`；脚本只能在 FunctionPreview 缓存 fetch 精确路径并在本次 `.tmp` 原子输出。
- LFS/正式 workbook 无法物化时，相关配置需求为 `无法确认`；不得改用生成 JSON 或旧文档形成确定性结论。
- 若同一 config target SHA 存在该表的直接生成 JSON，可导出到本次 `.tmp` 并调用 `scripts/validate-config-json.py` 检查字段、主键、区间和权重；结果写入 `configurationChecks`，显著标为次级证据且不能替代正式 XLSX，相关正式表需求仍为 `无法确认`。
- 对物化副本使用 `config-table-editor` 只读解析；K1 禁止 `xcfg-tool`。
- 在需求证据完成映射后，调用 `scripts/review_rule_matcher.py`，输入 `references/k1-review-rules.json`、当前 PrecheckResult 和本次 `collect-git-evidence.ps1` 的冻结输出。规则按仓库角色、需求已映射路径和需求信号叠加命中，不采用首条命中即停止。
- 没有映射证据的需求不得回退到该仓库全部 changed paths 触发路径规则；仍可由需求信号触发。
- 路径 glob 中的 `**/` 表示零层或多层目录，因此同一规则同时覆盖仓库根目录文件和嵌套文件。
- 为每个选中的 `checkId` 写一条 `reviewChecks`，状态只能是 `已核对`、`不适用` 或 `无法确认`。`已核对` 必须带可定位证据；`不适用` 必须说明理由且不能带证据；`无法确认` 必须说明缺失证据和补证动作。
- 规则的 `rolesAny`/`rolesAll` 决定触发与主证据角色，`evidenceRoles` 只扩展允许引用的辅助仓库。`已核对` 必须包含主角色证据，跨端 `rolesAll` 必须覆盖其中每个角色。
- collector 对规则涉及的任一角色返回 error/requires-input 时，该规则检查必须为 `无法确认`；不能用其他成功端的证据标为 `已核对` 或 `不适用`。
- 规则定义检查范围，规则命中和核对状态不得直接决定需求结果、finding 类型或总体结论；结论仍由开发文档与已核验证据决定。

### 6. 终检与发布

- 再次调用 `scripts/snapshot-repository-state.ps1`，比较 before/after digest。
- 构造 `readonlyCheck`：`contractPassed` 表示所有可能写 Git/LFS 的子进程是否仅指向 FunctionPreview；`workspaceChanged` 表示正式工作区 before/after 是否不同。
- `source=remote` 时，用户切分支、提交或继续编辑只做披露，不污染已冻结 SHA 的结论；不得描述成工作流写入，也不得因此强制 `预检信息不足`。
- `source=local` 时，`workspaceChanged=true` 仍强制 `预检信息不足`。任一模式 `contractPassed=false` 都强制 `预检信息不足`。
- renderer 使用同一冻结 Git 证据重新计算规则选择。缺失、重复或多余的 `reviewChecks`、采集失败角色未标为 `无法确认`、证据来自规则无关角色，或其他状态与证据合同不符时，发布失败且不创建报告目录。
- 发布前，代码/文本证据必须包含冻结 target SHA 和完整行原文 `snippet`；将本次角色、仓库路径、target SHA 的 manifest 通过 `--evidence-manifest` 传给 `scripts/render-fast-precheck.py`。其 `scripts/evidence_anchors.py` 从冻结 Git 对象强制校验位置；唯一匹配可修正行号，不存在或多处匹配必须补证，或把证据所属条目标为 `无法确认` 并提供 `unverifiedReason`，不得保留确定性发现。
- 将 `collect-git-evidence.ps1` 的原始冻结输出通过 `--git-evidence` 传给 renderer；规则目录默认使用 `references/k1-review-rules.json`，需要显式重放时才传 `--review-rules`。
- 每条代码定位校验独立默认 30 秒，与工作流累计耗时无关，不触发 lazy fetch；缓存缺少对象时明确降级。正式 Excel 仍走原有表格核对。定位通过不代表业务判断成立。
- renderer 必须校验已完成的 `alignment`、三端版本、文档回读版本和 `testcaseDocumentVersion` 一致，未决差异或未完成回写不能发布预审报告。
- 活动发布还须通过生命周期结构、调用链引用、独立副作用断言和补验来源覆盖门槛。unknown 有明确承接时可发布带缺口报告；不能用入口存在或正确行号冒充业务闭环。旧活动 JSON 重新发布须在新副本补合同，旧报告不覆盖。
- 调用 renderer 只在新目录发布 `summary.html`、`review.md`、`testcases.md`；HTML 是默认阅读入口。旧 HTML/Markdown 保持可读，不重写；旧 JSON 若重新发布则必须符合新的校验合同。
- 预检结束且文档已确认、回读通过后，按 [文档确认标记](references/feature-experience.md#预检后文档确认标记) 更新本功能经验档案，保存文档来源、版本/内容哈希、确认时间与预检批次/证据。预检存在实现问题不等于文档未确认；文档标记也不代表功能验收通过。

### 7. 交接运行验收（用户请求时）

- 保存本次 `PrecheckResult` 输入 JSON，交接文档版本、完整用例及稳定 ID、冻结三端 manifest、已确认决定、发现和未知项；不要仅交 HTML 摘要。
- 活动运行计划以 `lifecycleAssertionId` 逐条承接基线独立断言；passed 必须记录每项 `observedEffects` 和运行证据。补验结果由关联断言派生，阻塞、排除和遗漏仍保持 open，不通过精简基线或改验收模式删除义务。
- 按 `references/runtime-acceptance.md` 确定用户指定的验收节点、客户端路径和文档状态，再为所选路径建立对应范围的断言计划及状态台账，使用 `assets/runtime-plan.json`、`assets/jenkins-test-request.json` 填写实际数据。
- 执行文档标记核验 → 用户指定节点与范围 → Mac 优先的配置表/多语言转换 → 分别启动并核验所选路径的专属服务器 → 对应 Unity 编辑器接入或真机包构建安装 → 所选路径各自编排和执行正常业务验证 → 自动补验 → 清理核对 → 按模式发布运行报告 → 文档回读与过程文件清理。Jenkins 与 GM 是环境准备路径，不能替代被测业务结果。
- 最终交付前可继续补验项必须为零；剩余未验分支必须有真实阻塞、用户排除或执行遗漏记录。失败项仍需继续其他独立分支。

## 静态结论词汇

- 需求结果仅用：`静态证据充分`、`存在明显缺口`、`证据不完整`、`无法确认`。
- 发现仅用：`阻断`、`风险`、`无法确认`。
- 总体结论仅用：`可进入运行验收`、`建议修正后再提测`、`预检信息不足`。
- 有直接证据的关键缺口或跨端契约冲突 → `阻断` + `建议修正后再提测`。
- 无阻断且核心需求有足够直接静态证据 → `可进入运行验收`。
- 文档不可读、工作流只读合同失败、本地证据模式变化或核心需求整体无法判断 → `预检信息不足`。

不要报告代码风格、泛化维护建议、非需求重构、广泛推测或低价值 P3。

## 静态完成条件

- 已先完成需求对齐；仅已确认的需求调整更新原文档，回读核验成功，变更记录与差异清单可追溯。
- 用例与预审依据对齐后的同版文档、同组三端 SHA；未回写项已交接核查。

- 报告对象是本次从实时 `origin` 冻结的 ref/SHA，而非本地当前分支或旧 tracking ref。
- 本地三端可以位于任意分支并保留未提交改动；远端模式允许用户在审核期间继续工作。
- 正式 K1 仓库没有工作流写入；所有 fetch/LFS 写入均位于 FunctionPreview 缓存。
- 开发文档每项需求都出现在矩阵中；未知项包含原因与运行验收动作。
- 所有叠加命中的规则都有一条且仅一条 `reviewChecks` 审计记录。
- 三份非空报告发布到唯一新目录且旧报告未覆盖。
- 对话返回总体结论、阻断/风险/未知计数、耗时、`summary.html` 链接和非验收声明；另用一句说明功能档案更新结果及待回写项。
