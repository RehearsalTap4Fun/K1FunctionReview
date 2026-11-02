# 巨蛇大作战4期：验收经验档案

| 字段 | 内容 |
|---|---|
| featureId | k1-giant-snake-phase4 |
| 别名 | 肉鸽塔防4期、巨蛇4期、Phase4Minion、混合无尽 |
| 关联需求 / 分支 | NK-10652、NK-10657 / dev_NK-10652 |
| 更新时间 | 2026-11-02，Asia/Shanghai |
| 最近实际验证 | 仅静态取证与环境核查；业务运行尚未执行 |

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
| S-01 | K1FunctionReview/.tmp/k1-nk10652-20261102-unity；客户端21cf159a3edf48da49716ede0ccb154ab84c56f5、正式配置9f4436eb149816db6dbf4cde5c9260ac09fd3c78 | 本机原始证据，不随Skill分发；10份工作簿经Git LFS OID/大小校验，85项用例仅已编排。 |

## 已核实的定位与待验证项

| entryId | 事实或方法 | 状态与下次动作 |
|---|---|---|
| CFG-LEVELS | ActivityDragonRoguelikeLevel.xlsx的ActDragonBattleLevelCfg为40普通关＋41挑战；布局24底部/16中心，10小兵关包含11/25两纯兵关。 | 2026-11-02静态核对；运行入口、解锁与胜负仍需实测。 |
| CFG-PROJECTILES | DragonRoguelikeSkill.xlsx的ActivityProjectileParams与客户端Phase4Projectiles.json需逐参数比较；当前水环baseHarm/appendBaseHarm为5.2/6.0与6.5/7.5两组。Phase4BeamRuntime.TryLoadSettings读TextAsset，Phase4RingRuntime消费settings.ring。 | 静态差异已核实；实际加载值、伤害和正式导出映射待验证，禁止手工改生成配置。 |
| CFG-INSTANCE-GUARDS | Phase4MinionConfigStore、Phase4ShieldConfigStore、Phase4EndlessConfigStore按TextAsset.activityIDs检查实例。 | 静态核对；新活动开测先读实际实例ID，分别经正式入口验证兵/盾/无尽，预览成功不能替代。 |
| ENV-DEPLOYMENT | 同名服务端分支缺失时，可由真实Jenkins构建参数定位已部署代码与配置；最新dev和当前运行提交可能不同。 | 方法已用于只读核查；以本轮镜像、构建、实际配置交叉确认，不默默回退分支。 |
| TOOL-ASYNC-REFLECTION | EditorDebugMCP v0.1.0的invoke返回Task本体时，序列化器可能读取Task.Result并阻塞编辑器；本轮调用后编辑器无响应，根因尚待进一步验证。 | 避免返回Task本体；必要异步启动后链式读取IsCompleted等非阻塞值。无响应时保留状态并按本轮权限确认恢复，不能把连接注册当作可执行。 |

## 运行与界面覆盖

本轮用例包括三种弹道、盾计次、3/1调度、预算与去重、双源宝箱、复活读档、旧期次、生命周期副作用、英/俄/阿、ESC与Unity屏幕尺寸。尚未获得业务、三语或返回操作通过证据；真机仅在用户明确指定时纳入。没有可复用的已验证游戏操作脚本。

私有反馈来源、账号、目标服、环境权限、清理与恢复状态均读取S-01，不写入共享Skill。
