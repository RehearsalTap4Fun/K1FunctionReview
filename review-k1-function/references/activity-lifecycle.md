# 活动全生命周期、独立结算断言与补验合同

活动类功能在需求对齐后、拆用例时建立本合同，保存在同一 `PrecheckResult`。模板为 [activity-lifecycle.json](../assets/activity-lifecycle.json)，与现有 `requirements`、`testcases`、`findings` 及文档版本一起维护。填写真实来源和稳定 ID；模板不是通过证据。

## 1. 识别与范围

活动任务设置 `metadata.featureType="activity"`。发布器也根据需求／用例中的“活动”、英文 activity 及相关服务端／配置路径识别；删掉类型字段不能绕过明显的活动输入。纯局内“单局结算”不单独触发活动合同。自动识别不能替代人工判断，未知命名的活动应显式设置类型。

全生命周期均要有槽位，无关阶段用 `not_applicable` 加原文依据说明。不能因为未在 diff 中改动，就省略结束、回收或关闭流程。生命周期覆盖、静态实现正确、实际业务验收通过是三个不同结论。

旧 HTML／Markdown 保留可读。旧活动 JSON 重新发布或建立运行验收计划，必须新建补齐合同的副本；不覆盖旧证据，不修改已经执行的旧计划哈希，也不提供跳过生命周期校验的开关。

## 2. activityLifecycle（schemaVersion=1）

### stages：每种 ID 恰好一条

| ID | 阶段 | checked 必须记录的 chain.step |
|---|---|---|
| start | 开启 | trigger、handler、effect |
| active | 进行 | handler、guard、effect |
| end | 到期结束／中止在途行为 | trigger、handler、guard |
| settlement | 发奖与补发 | trigger、handler、dispatch、effect、persistence、failure |
| recovery | 资产回收／补偿 | handler、effect、persistence、failure |
| close | 关闭与进度清理 | trigger、effect、persistence |
| next_cycle | 下一期隔离 | trigger、guard、effect |

阶段字段：`id`、`status`，以及下表所需字段。

| status | 必需记录 |
|---|---|
| checked | 非空 `requirementIds`、`reason`；完整 `chain` |
| unknown | 非空 `requirementIds`、`reason`；`followupObligations` 必须承接 `stage:<id>` |
| not_applicable | `reason`、可回到原文的 `documentLocator`；不能附检查通过的 chain |

`chain` 每步包含 `step`、说明代码如何支持结论的 `explanation`、非空 `evidenceRefs`。引用格式为 `{"requirementId":"REQ-END","index":0}`，指向该需求 `evidence` 数组的第 0 项；引用的需求必须属于阶段 `requirementIds`。只能使用具有完整 snippet、未降级的服务端代码证据，仍由发布器校验冻结 SHA／实际源码锚点。

完整链至少有两个不同源码锚点，不能把同一 OnEnd 转调片段复制到所有步骤充当闭环。阶段尚未查全时填 unknown 并说明停在哪一步；不能用“运行才知道”略过可从源码继续追踪的调用者、异步回调、存储、失败处理与清理。

**语义检查由审查者负责**：正确行号不代表代码证明该业务结论。尤其不能用发奖入口证明数据删除，也不能用请求已发送证明邮件持久化成功。结构校验不会自动理解任意代码的业务含义。

### assertions：独立可执行预期

以下六种 `kind` 均需出现。一个 kind 可以拆成多个场景，但每条必须有独立 ID。确实不适用时只保留一条 `applicability=not_applicable`，填写 `reason`、`documentLocator`，不带 `testcaseIds`。不得以“本轮不测”冒充规则不适用；本轮排除在运行结果中记录用户决定。

| kind | 必需 observables（可以增加） |
|---|---|
| rank_reward | mail_count、attachments、asset_delta、duplicate_delivery |
| unclaimed_reward | eligibility、mail_count、attachments、asset_delta、duplicate_delivery |
| peripheral_reward | eligibility、mail_count、attachments、asset_delta、duplicate_delivery |
| asset_recovery | before_after_inventory、late_delivery |
| progress_cleanup | before_after_progress、next_cycle |
| unfinished_round | result_state、no_new_rewards |

适用断言字段：`id`、`kind`、`applicability="required"`、`requirementIds`、`testcaseIds`、`expected`、`action`、`observables`、`requiredEvidence`。每条断言的 `testcaseIds` 必须恰好包含一个用例，多个场景拆成多条断言；同一用例可以有多个独立断言。需求与用例引用必须存在且互有关联。证据类型使用现有运行类型；上述六类必须包含 server／runtime／platform 至少一种，不允许只有截图、协议成功码、静态或 GM 证据。

`expected`、`action` 写完整条件、独立副作用和异常预期。应拆在线／离线、已领／未领／未达、排名档位、失败重试、重启恢复、晚到资产等实际适用场景；类型槽位存在不代表这些场景已全部测试。资产未变化也要记录期望为零的差值。外围模块不发邮件时，邮件观察记录确实未发，不能借此跳过外围资产核对。

其他需求的补验使用 `kind="requirement"`（可多条），自定义非空 observables，可使用 UI 等运行证据。用于界面、重连、普通玩法等未决项，不能把它们强塞进结束发奖断言，也不能取代上述六类。

## 3. followupObligations：独立于产品缺陷表

每项含 `id`、`sourceRefs`、`requirementIds`、`assertionIds`、可执行 `nextAction`、可核对 `closureCriteria`。

必须承接以下来源，每种来源都要有去向：

- `requirement:<id>`：结果不是“静态证据充分”的需求。
- `finding:<id>`：活动预审中的每条发现，包括阻断、风险与无法确认；不因不进入产品缺陷表而删除。
- `stage:<id>`：unknown 生命周期阶段。
- `external:<id>`：文档更正或历史交接的额外义务。先在顶层 `followupSources` 登记 `id`、`requirementIds` 和 `description`，例如尚未进入本轮 finding 的旧补验项。

`assertionIds` 必须指向本合同中 required 的独立断言，覆盖其关联需求。可以合并重复的准备操作或相同来源，但不能合并掉独立预期。没有下一步、没有完成标准、没有绑定断言的“以后验证／随相关问题处理”不能发布。

产品规则尚未确定，仅阻塞相应断言；已经明确的奖励、回收义务继续独立检查。更换文档、切换验收模式或精简反馈描述时，稳定来源 ID、断言和义务必须随交接保存。旧义务确实失效时，在来源与用户决定中保留原因，重新对齐后建立新版本，不能直接删除以获取通过。

## 4. 发布门槛与运行交接

预审发布在创建报告目录之前检查：全阶段槽位、检查链、独立断言、双向需求／用例引用及补验来源覆盖。unknown 有明确补验去向时允许发布带缺口的静态报告；不能把它改成 checked。HTML 和 Markdown 展示生命周期及补验表。

结束／补发等信号以及已关联的阶段需求，会在规则匹配中展开为“活动生命周期”，触发时间边界、状态流转、持久化和幂等检查；依旧是叠加命中，不以第一条规则替代其他检查。

运行计划继续使用 schemaVersion=2 及原 `baselineFile`／SHA256。活动 baseline 必须保留完整 `PrecheckResult` 合同；不能只拷贝几条体验用例，丢掉 `requirements`、`activityLifecycle` 和 `followupObligations`。每条 required 断言在运行计划中恰好绑定一次：

```json
{
  "id": "TC-END/rank-mail",
  "testcaseId": "TC-END",
  "lifecycleAssertionId": "END-RANK-MAIL",
  "expected": "与基线该断言的 expected 完全一致",
  "action": "与基线该断言的 action 完全一致",
  "phase": 1,
  "dependsOn": [],
  "requiredEvidence": ["server"]
}
```

不要靠改写一句“已结束即可”弱化 expected，不能减少 requiredEvidence。新版本确实改变预期时重新建立并核对基线。推进时间前仍运行 `check-advance`；测试服操作授权边界不因新增断言自动扩大。

运行结果置 passed 前，为每个 observable 填 `observedEffects`，逐项提供实际观察和非空证据文件，例如：

```json
{
  "observedEffects": {
    "attachments": {
      "observation": "填写邮箱邮件 ID、附件物品与数量，和已确认配置的对照结果",
      "evidence": [{"kind": "server", "path": "mail-and-inventory.json"}]
    }
  }
}
```

这个片段只演示一项；实际必须补齐该断言全部 observables。每个观察项自身的证据必须满足该断言声明的全部 requiredEvidence；六类结算观察至少有 server／runtime／platform 证据，不能借用断言顶层的其他证据补足。仅协议成功码、静态、GM 或截图不能证明邮件与资产副作用。实际文件内容的真实性及观察与预期是否相符仍由执行者核对，门槛不把虚构文本转为真实结果。

`followupResults` 由断言结果派生：全部关联断言 passed 才为 verified；失败、阻塞、明确排除或执行遗漏均为 open，报告保留来源、下一步和关闭标准。真实阻塞可按现有合同结束本轮，但不能 fullyAccepted；可继续项仍阻止发布。结论只针对当前模式及完整计划范围，部分体验不关闭旧补验义务。
