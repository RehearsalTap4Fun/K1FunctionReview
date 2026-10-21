# AI 验收工作流

入口：`python -X utf8 review-k1-function/scripts/acceptance_workflow.py <领域> <动作> --request <JSON> --run-dir <本轮目录>`。

Agent 在使用这些命令前按 [经验读写规则](feature-experience.md) 读取 [本功能档案](../features/index.md)，在阶段完成或中断前更新档案与必要脚本说明。CLI 维护的运行状态与证据继续独立保存，不把 `runtime reuse` 或 `publish` 当成经验自动回写。

`run init/show` 管理版本基线；`evidence add/review/verify` 登记内容哈希与实际看图记录；`operation next` 列出待执行或待核对动作。派发后没有回执时必须回读目标，不可直接重复发送。

`feedback snapshot/plan/apply/reconcile` 使用 DWS 的真实工作表 ID、有限读取范围和 sidecar 问题身份。快照需要完整图片导出与原始下拉对象。每次修改只写验收与必要详情，截图生成浏览器 `append_cell_images` 动作单；不能调用替换图片接口实现多图追加。浏览器执行前用 `operation dispatch` 留记录，再保存上传、逐图打开和导出核对证据。旧图片、开发状态、下拉选项/颜色/顺序/范围/未知属性均参与比较。导出失败不自动重试，不将图片覆盖未知当作无图片。

`fixture list/plan/verify/cleanup-plan` 使用限定账号/SID/活动/当前局的授权和状态。预算按原授权 scopeId 跨批次共用；未知结果不释放预留。清理只恢复本前置负责且随后未改变的字段，有冲突先保留现场。GM 回执不等于业务验收通过。

已验证层级和真实环境条件应在各自私有交付报告中记录；示例和单元测试不代表业务验收通过。具体测试服及允许的配置范围以当前用户授权为准。
