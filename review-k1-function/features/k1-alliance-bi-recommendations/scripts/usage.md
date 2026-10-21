# 联盟 BI 配置行提取脚本

归属：`k1-alliance-bi-recommendations`；[功能档案](../experience.md)。整理日期 2026-10-21，Asia/Shanghai。该脚本读取离线工作簿副本，不连接游戏或数据平台，不执行邀请、踢人或发邮件。

## 版本与来源

| 字段 | 内容 |
|---|---|
| scriptId / 唯一文件 | BI-S01 / [inspect_config.py](inspect_config.py) |
| 来源 | `FunctionPreview/.tmp/nk8728-20260804-193040-370f68fb/inspect_config.py`，原字节复制 |
| 当前及来源 SHA256 | `091177db305d41c8d1ae27eb37c94018a242935479b18eb30bee792f8775414d` |
| 历史业务批次 | 2026-08-04 静态预检，配置 target `022615dc98f75de6a82baa211c9dcb3c1bccfd45`；不是运行验收 |
| 本次实际执行 | 2026-10-21，原批次留存的三张 XLSX 副本；Python 3.12.14 + openpyxl。未读取或修改正式仓库 |

哈希是整理时所读文件的字节哈希；源报告没有执行当时的独立脚本哈希。此次同字节离线重跑提供独立提取证据，不刷新历史业务结论。以后改动 ID、表结构或逻辑时更新哈希、原因与验证范围。

## 参数、宿主和开始状态

宿主是本机 Python 3，依赖 `openpyxl` 和标准库 json/sys/pathlib。只有一个必填位置参数：**包含三张工作簿副本的目录**。脚本没有命令行选项或环境变量，也没有 Unity/账号/SID/凭证参数。

输入目录必须包含以下精确文件名：

| 文件名 | 固定历史筛选范围 |
|---|---|
| `ConstConfig-materialized-target.xlsx` | 首列 ID 10135700–10135751 |
| `NewMail-materialized-target.xlsx` | 首列 ID 10950114、20000012、20000015、17112009、17112010 |
| `Switch-materialized-target.xlsx` | 首列 ID 336–343 |

按 `config-table-editor` 的 K1 Excel 约定取得本轮冻结版本的副本，不在正式仓库重命名表。第 3 行是字段名，第 9 行起是数据；遍历所有 sheet，仅返回命中首列 ID 的 sheet。使用 `read_only=True, data_only=True`，公式读缓存值，既不计算公式也不保存工作簿。缓存缺失、表头变化或 ID 变化时需要人工核对，空命中不等于配置缺失或通过。

调用示例（PowerShell；两个路径均替换为本轮实际路径）：

```powershell
python -X utf8 '<本轮脚本副本绝对路径>' '<本轮工作簿副本目录>'
```

先复制唯一脚本到本轮 `.tmp/<run-id>/`，核对输入文件版本和哈希，再调用。stdout 是完整 JSON，调用方以 UTF-8 保存到本轮新的证据文件；脚本没有输出文件参数或防覆盖逻辑。不要把工作簿或输出回拷到 Skill。

## 输出与结果判断

正常结束为退出码 0 且 stdout 可解析为 JSON；三个工作簿键均存在，命中项包含行号及按第 3 行映射的非空字段，sheet 包含 dimensions/header_rows/matches。JSON 中 `sha256` 固定为 null，**不是版本校验**；输入哈希必须另行计算和记录。

脚本只做历史 ID 抽取，没有判断业务对错：比如 20000015 没命中，需要结合当前邮件引用和替代 ID；开关 336–343 都命中仍可能是错位使用。按实际字段语义与需求、枚举消费者逐条核验。

## 副作用、停止与清理

- 只读输入并向 stdout 输出；不写文件、不调用外部服务、没有回调或后台任务。原实现没有显式 `wb.close()`，进程结束后释放句柄，异常后先确认进程退出再处理文件。
- 无内置超时；调用方按表大小设置进程超时，停止可中止本轮 Python 进程。失败或输出截断保留 stderr，用新证据文件重跑，不能将半段 JSON 当作结果。
- 本轮副本和输出按证据留存要求处理，不改历史工作簿或原始报告；输出可能含业务配置，只留在本轮受控目录。

## 2026-10-21 离线验证

重跑来源目录的三张历史 XLSX 副本，核对输出行号与独立只读筛选一致，脚本与原文件字节一致，三份输入前后哈希不变：

| 工作簿 / sheet | 命中行数 | 输入 SHA256 |
|---|---|---|
| ConstConfig / ConstConfigCfg | 52 | `7c53a46130830699cc9d2582dbe8753072d7f088686dc92542e7bbbdc980114e` |
| NewMail / NewMailCfg | 4 | `78dcd4793b456d0ada793562c78fac7d19caa3c96b6aef7a508015139ed69f9a` |
| Switch / D2SwitchCfg | 8 | `ba7b6b3ec0cd9bdfed103f8d8d6c37d3d884a867866fdb7da2e7bf400e8bb5d5` |

openpyxl 报工作簿无默认样式并应用读取默认样式，退出码仍为 0，输入未被改写。回执位于 `FunctionPreview/.tmp/feature-archive-20261021/bi/verification.json`，完整输出为同目录 `config-inspection.json`。这些只证明历史副本上的提取行为，未验证当前配置、BI 接口或游戏业务。
