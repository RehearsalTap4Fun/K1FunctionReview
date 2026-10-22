# K1 项目测试用例配置

> K1 项目的测试用例生成配置。

---

## 项目基本信息

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 项目名称 | `K1` | K1 项目 |
| 项目代号 | `K1` | （配置表前缀仍沿用 `p2_`，与 Google Drive 实际名一致）|

---

## Google Drive 路径配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 用例根目录 ID | `1wtQhEaTrW2B6E9uLm_lnyT8XNiZ2dKbJ` | Google Drive 中存放用例的根文件夹 |
| 用例模板 Sheet ID | `13bh-0fnsqusJlkRI284rBOG89-pnFH2VyY5NqiD5ScA` | 用例模板文件 |
| 凭证文件名 | `brutal-age-64236173-4ce5d8c0ebb5.json` | OAuth 凭证文件 |

> **目录结构**：根目录/ → 年份/ → 周期文件夹/ → 用例文件

### 用例文件命名规则

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 命名格式 | `{周期编号}_AI_{功能名称}` | AI 生成的用例文件命名 |
| 周期编号提取 | 从周期文件夹名提取数字 | 如 `565（3.9~3.13）共5D` → `565` |

**示例**：
- 周期文件夹：`565（3.9~3.13）共5D`
- 功能名称：`情人节组队活动_相伴生长`
- 最终文件名：`565_AI_情人节组队活动_相伴生长`

---

## 配置表路径配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 配置表总文件夹链接 | [Google Drive](https://drive.google.com/drive/folders/18fRVYlkXD7hhfQbeYhePDd-upXPF5EyJ) | 所有配置表根目录 |
| 配置表释义 Sheet ID | `1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c` | 配置表释义文档 |
| 配置表释义分页名 | `fw_gsheet_config` | 释义文档中的分页 |

### 配置表文件夹结构

```
Google Drive 配置总文件夹/
├── 10_p2_const/           # 常量配置
├── 11_p2_asset/           # 资产配置
├── 12_p2_status/          # 状态配置
├── 13_p2_map/             # 大地图配置
├── 14_p2_quest/           # 任务配置
├── 15_p2_art_res/         # 美术资源配置
├── 16_p2_battle/          # 战斗配置
├── 17_p2_features/        # 功能配置
├── 18_p2_union/           # 联盟配置
├── 19_p2_hero/            # 英雄配置
├── 20_p2_iap/             # 内购配置
├── 21_p2_event/           # 活动配置
├── 22_p2_notification/    # 通知配置
├── 23_p2_situation/       # 情境配置
├── 24_p2_satellite_battleground/  # 卫星战场
├── 25_p2_kvk/             # KVK配置
├── 26_p2_expedition/      # 远征配置
├── 27_p2_minigame/        # 小游戏配置
├── 28_p2_defence_game/    # 防守游戏
├── 29_p2_train_gvg/       # 训练GVG
├── 30_p2_monkey_takeover/ # 猴子接管
├── 31_p2_boss_rush/       # Boss Rush
├── 32_p2_kvk2/            # KVK2配置
├── 33_p2_team/            # 队伍配置
├── 34_p2_soldier_skill/   # 士兵技能
├── 35_p2_metro_minigame/  # 地铁小游戏
├── 36_p2_dungeon_warfare/ # 地牢战争
├── 37_p2_oap/             # OAP配置
├── 38_p2_kvk3/            # KVK3配置
├── 39_p2_arm_expedition/  # 武装远征
├── 40_p2_mecha_system/    # 机甲系统
├── 41_p2_soldier_battleground/    # 士兵战场
├── 42_p2_mech_battleground/       # 机甲战场
├── 43_p2_racegame/        # 竞速游戏
├── 44_p2_topwar/          # TopWar
├── 45_p2_kvk4/            # KVK4配置
├── 46_p2_evolved_cards/   # 进化卡牌
├── 47_p2_tank/            # 坦克配置
├── 48_p2_shoot/           # 射击配置
├── 49_p2_minigame_common/ # 小游戏通用
├── 50_p2_line_builder/    # 线路建造
├── 51_p2_kingland_battleground/   # 王国战场
├── 52_p2_mecha_battleground_v2/   # 机甲战场V2
├── 53_p2_mob_control/     # 怪物控制
├── 54_p2_tower_defense/   # 塔防配置
├── 55_p2_tank_battleground/       # 坦克战场
├── 56_p2_special_hospital/        # 特殊医院
├── 57_p2_city_territory/  # 城市领地
├── 58_p2_kvk5/            # KVK5配置
└── 59_p2_rougue_castle/   # 肉鸽城堡(MJ9)
```

### 常用配置表速查

> 来源：[常用配置表分页](https://docs.google.com/spreadsheets/d/1vCJd9r9Z50uEwwpcUc-5qlCnasPxpDej2YUnHmplf04/edit?pli=1&gid=343483927#gid=343483927)

| 配置表ID | 测试场景 | 表格名称 | 主要用途 |
|:--------:|----------|----------|----------|
| 1111 | 道具 | 1111_p2_item | 背包道具、可消耗道具 |
| 1114 | 道具 | 1114_p2_rss | 食物、钢铁、胶囊、机甲经验等个人资产 |
| 1115 | 道具 | 1115_p2_vm | cd、军功币等货币 |
| 2112 | 功能 | 2112_p2_activity_config | 所有活动id、展示奖励 |
| 2111 | 活动 | 2111_p2_activity_calendar | 活动开启条件、持续时间 |
| 1013 | 功能 | 1013_p2_const_config | 多数功能、限制等条件 |
| 1023 | 功能 | 1023_p2_popwindow | 弹窗的优先级、弹出条件 |
| 2011 | 礼包 | 2011_p2_iap_config | 礼包优先级、时间、显示条件 |
| 2013 | 礼包 | 2013_p2_iap_template | 礼包本地化、价格、限购、道具 |
| 1018 | 功能 | 1018_p2_ab_test | AB测试配置 |
| 1768 | 功能 | 1768_p2_chapter_quest_function_unlock | 功能解锁条件 |
| 2137 | 活动 | 2137_p2_activity_asset_retake | 活动道具回收表 |
| 1119 | 研究 | 1119_p2_research | 研究所科研buff |
| 1920 | 功能 | 1920_p2_hero_data | 斗士相关配置 |
| 1153 | 道具 | 1153_p2_get_access | 获取途径显示条件 |
| 2136 | 活动 | 2136_p2_activity_cycle_period | 活动斗士期数 |
| 1165 | 功能 | 1165_p2_stores | 全部商店排序、解锁条件 |
| 2115 | 活动 | 2115_p2_activity_task | 活动任务达成条件 |

---

## 项目特色玩法知识库

> K1 项目特有的玩法系统知识文件，存放在 `testcase-config/game_knowledge/` 目录下。

### 关键词触发规则

| 关键词 | 触发知识库 | 文档路径 |
|--------|------------|----------|
| 红色英雄、共享、同频 | 红色英雄系统 | `testcase-config/game_knowledge/red_hero_system.md` |
| 背后灵、助战、附身、参谋 | 背后灵系统 | `testcase-config/game_knowledge/backspirit_system.md` |
| 战车、舱位、槽位 | 战车系统 | `testcase-config/game_knowledge/tank_system.md` |
| 推币机、投币、弹珠 | 推币机玩法 | `testcase-config/game_knowledge/coin_pusher_system.md` |

### 通用知识补充文件

> 以下文件补充通用框架中 K1 特有的副本名/数值/Tips 等细节。

| 补充文件 | 对应通用框架 | 内容 |
|----------|-------------|------|
| `K1_battle_details.md` | `battle_system.md` | K1 副本名称列表、来源用例编号 |
| `K1_hero_details.md` | `hero_system.md` | K1 品质体系、等级/星级上限、Tips 文案 |
| `K1_redpoint_details.md` | `redpoint_system.md` | K1 红点层级结构 |
| `K1_cross_server_details.md` | `cross_server_system.md` | K1 KVK 版本列表、KVK5 详细内容 |

---

## 人工用例样本

> 存放在 `testcase-config/doc/` 目录下。

| 样本 | 类型 | 用例数 |
|------|:----:|:------:|
| [沙滩寻宝](doc/0.84.0_张杨_沙滩寻宝_测试用例.md) | D | 290条 |
| [新机甲鳄鱼](doc/0.80.0_阮邦武_新机甲鳄鱼_测试用例.md) | A | 589条 |
| [红色英雄系统](doc/红色英雄系统用例思路分析.md) | A+ | ~1500条 |

---

## 变更记录 sheet 自动填写规则

每个用例文件的"变更记录" sheet 在生成时**自动填写**以下字段：

### 变更记录区（行 3）

| 单元格 | 字段 | 自动填入值 |
|--------|------|-----------|
| A3 | 时间 | 今日日期，格式 `YYYY.MM.DD`（如 `2026.05.25`） |
| B3 | 操作员 | `AI` |
| C3 | 操作内容 | `新建` |
| E3 | 操作说明 | `共 N 条`（N = 用例总数） |

### 评审详情区（行 8-9）

| 单元格 | 字段 | 自动填入值 |
|--------|------|-----------|
| C8 | 功能名称 | `<feature_name>`（脚本参数） |
| C9 | 设计人员 | `AI` |
| E9 | 定稿条数 | N（用例总数） |
| G9 | 功能类型 | 下拉选项之一（脚本参数 `feature_type`，默认 `功能优化`） |

### 功能类型下拉选项

```
通用用例 / 框架复用 / 新功能 / 新活动 / 大型&复杂系统 /
纯客户端 / 纯服务器 / 通识类 / 功能优化 / 检查点
```

### 用例 sheet A1 团队信息（自动）

| 单元格 | 字段 | 自动填入值 |
|--------|------|-----------|
| A1（A1:I1 合并）| 策划/客户端/服务器 | `策划：{F列}，客户端：{G列}，服务器：{H列}` |

数据来自跟踪表 `<周期>版本` sheet 中匹配到的功能行的 F/G/H 列。任一字段为空时显示 `无`。

### 用例 sheet B6 PRD 链接（自动）

| 单元格 | 字段 | 自动填入值 |
|--------|------|-----------|
| B6:E8 | SVN路径/参考文档 | 显示文本 = `<功能名称>`，整段加蓝色下划线超链接指向 `<PRD链接>` |

**PRD 链接来源（优先级）：**
1. 命令行第 4 个参数 `[PRD链接]`（显式指定，最高优先）
2. **自动从跟踪表 `<周期>版本` sheet 的 C 列提取**：脚本会按 feature_name 模糊匹配 C 列文本，自动取出 C 列的超链接

模糊匹配算法：
- 拆分 feature_name 的关键词（用 `_`、`-`、空格、括号分隔）
- 自动剥离通用后缀：`优化/活动/系统/功能/一期/二期/版本/新版` 等
- 别名映射：`龙吟沙漠 ↔ 巨龙之战`、`周年回顾 ↔ 周年庆/年报`、`克里斯/疯狂哈罗德 ↔ 哈罗德`
- 长 token 权重更高，阈值 ≥ 3 避免误匹配

> 找不到匹配时保留 B6 模板提示文字不变，会在日志中提示。

### 调用方式

```bash
python scripts/write_cases_to_sheet.py <json_file> <功能名称> [功能类型] [PRD链接]
# 示例（无 PRD 链接）
python scripts/write_cases_to_sheet.py output/case.json 龙吟沙漠二期优化 功能优化
python scripts/write_cases_to_sheet.py output/case.json 周年回顾 新功能
# 示例（含 PRD 链接，B6 自动填）
python scripts/write_cases_to_sheet.py output/case.json 周年回顾 新功能 https://jira.tap4fun.com/browse/NK-6539
```

---

## 跟踪表自动更新规则

### 跟踪表信息

| 配置项 | 值 |
|--------|-----|
| 跟踪表 ID | `1PuOpAhfByj6-B_JUb_2tcQr4DfQJqAIq9iauubJMTC0` |
| 对应 sheet 命名 | `{周期编号}版本`（如 `577版本`） |
| 行匹配规则 | 用提测内容（C 列）与生成的功能名做模糊匹配 |

### 更新规则

用例写入 Sheets 完成后，**自动**更新跟踪表对应行：

| 列 | 字段 | 写入内容 |
|----|------|---------|
| I | 用例编写人 | **保持 `AI` 文本不变**，把 `AI` 文本变成超链接（蓝色+下划线），链接指向生成的用例 Sheet |
| J | 用例情况 | `已完成` |

> ⚠️ **重要**：I 列只写 `AI` 这两个字符（不要追加功能名、不要写成 `AI - xxx` 之类）。如果该行已经有 `AI` 文本，只需要给它加上超链接。

### 富文本格式参数

```python
{
    'userEnteredValue': {'stringValue': 'AI'},
    'textFormatRuns': [{
        'startIndex': 0,
        'format': {
            'foregroundColor': {'red': 0.067, 'green': 0.333, 'blue': 0.8},
            'underline': True,
            'link': {'uri': '<用例 sheet 链接>'}
        }
    }]
}
```

---

## 备注

- K1 项目使用竖屏模式
- 英雄在 K1 中称为「斗士」
- 配置表前缀统一为 `p2_`
