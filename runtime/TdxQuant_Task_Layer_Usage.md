# TdxQuant Task Layer 使用说明

本文记录第二阶段新增的 task 层入口，用于把高频 API 组合流程收敛成稳定日常命令。

## 1. 顶层定位

当前有三个相关顶层入口：

- `TdxApiManager`
  - 面向原子能力
  - 适合脚本、调试、精细控制
- `TdxTaskManager`
  - 面向稳定场景
  - 适合日常高频调用
- `catalog`
  - 面向跨 `report` / `trade` / `task` 的统一日常入口
  - 适合把常用 preset 再收口成更短命令，或把固定多步流程收口成 bundle
  - 执行前还能用 `catalog plan` 做零副作用预览
  - 日常查看时还能用 `catalog list --view summary` 快速发现入口
  - 执行或预览后还能用 `--view summary` 输出更短结果

边界约定：

- task 层只做编排，不直接调用 `bridge.py`
- task 层内部通过 `TdxApiManager` 调用 `market/meta/formula/block`
- task 层现在可以同时编排 `TdxApiManager` 与 `TdxTradeManager`
- catalog entry 只做统一索引
- catalog bundle 只做既有 entry 的顺序编排，不新增底层 workflow 逻辑

## 2. Profile 文件

task 层使用独立配置文件：

- [runtime/task-profiles.json](/opt/iflow/TdxQuant/runtime/task-profiles.json:1)
- [runtime/task-presets.json](/opt/iflow/TdxQuant/runtime/task-presets.json:1)
- [runtime/report-presets.json](/opt/iflow/TdxQuant/runtime/report-presets.json:1)
- [runtime/command-catalog.json](/opt/iflow/TdxQuant/runtime/command-catalog.json:1)
- [runtime/command-bundles.json](/opt/iflow/TdxQuant/runtime/command-bundles.json:1)

当前内置 profile：

- `default`
- `sector_research`
- `formula_scan`
- `watchlist_overview`
- `watchlist_export`
- `sector_formula_scan`
- `sector_research_export`
- `trade_buy`
- `trade_submit_once`
- `guarded_trade_buy`
- `ledger_summary`
- `daily_trade_report`
- `trade_report_lookup`
- `trade_period_report`
- `maintenance`

其中：

- `api_profile` 用于指定 task 内部默认使用的 API profile
- `trade_profile` 用于指定交易 workflow 默认使用的 trade profile
- `gp_one_fields` 用于像 `sector-research` 这类场景里的批量字段默认值
- `export_dir` / `export_stem` 用于导出类 task 的默认文件落地规则
- `ledger_stem` 用于连续台账类 task 的默认文件定位规则
- `default_timezone` / `default_recent_limit` 用于日报类 task 的默认统计边界
- `refresh_before_trade` / `refresh_market` / `refresh_force` 用于交易 workflow 的预刷新编排
- `task-presets.json` 用于给稳定 task workflow 定义更短的日常别名
- `report-presets.json` 用于给 `report` 命令组定义更短的日常别名
- `command-catalog.json` 用于把 `report` / `trade` / `task` preset 再统一收口成单一日常入口
- `command-bundles.json` 用于把多个既有 catalog entry 继续收口成固定多步日常流程
  - 现在还支持 step `name`，方便局部执行和补跑
  - 现在还支持 `labels`，方便按用途筛选日常入口

## 3. Python 调用

```python
from tdxquant.api import TdxTaskManager

manager = TdxTaskManager(profile="sector_research", strategy_path="your_strategy.py")

result = manager.sector_research(
    block_code="钛金属",
    block_type=0,
    list_type=1,
)

print(result.to_dict())
```

公式扫描示例：

```python
from tdxquant.api import TdxTaskManager

manager = TdxTaskManager(profile="formula_scan")

result = manager.formula_scan(
    formula_name="MY_FORMULA",
    stock_list=["000001", "000002", "000333"],
    formula_arg="A,B,C",
    return_count=1,
)

print(result.to_dict())
```

板块同步示例：

```python
from tdxquant.api import TdxTaskManager

manager = TdxTaskManager(profile="default")

result = manager.block_sync(
    block_code="ZXG",
    symbols=["000001.SZ", "600519.SH"],
    mode="replace",
    create_if_missing=True,
    dry_run=True,
)

print(result.to_dict())
```

## 4. CLI 调用

### 4.1 板块研究

```bash
python -m tdxquant.cli task sector-research \
  --sector 钛金属 \
  --profile sector_research
```

可选参数：

- `--block-type`
- `--list-type`
- `--field`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前会做两步：

1. 调 `manager.meta.sector_stocks(...)` 获取板块成分
2. 从结果中提取证券代码，再调 `manager.meta.gp_one_data(...)` 拉批量字段

### 4.2 公式扫描

```bash
python -m tdxquant.cli task formula-scan \
  --formula-name MY_FORMULA \
  --code 000001 \
  --code 000002 \
  --profile formula_scan
```

可选参数：

- `--formula-arg`
- `--return-count`
- `--return-date`
- `--stock-period`
- `--start-time`
- `--end-time`
- `--count`
- `--dividend-type`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前直接编排 `manager.formula.process_mul_xg(...)`。

### 4.3 环境刷新

```bash
python -m tdxquant.cli task refresh-environment \
  --profile maintenance
```

可选参数：

- `--market`
- `--force`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前编排 `manager.refresh_cache(...)`。

### 4.4 自选/代码列表总览

```bash
python -m tdxquant.cli task watchlist-overview \
  --code 000001 \
  --code 000002 \
  --profile watchlist_overview
```

可选参数：

- `--field`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前直接编排 `manager.meta.gp_one_data(...)`，适合对一组固定代码做稳定批量总览。

### 4.5 板块同步

```bash
python -m tdxquant.cli task block-sync \
  --block-code ZXG \
  --stock 000001.SZ \
  --stock 600519.SH \
  --mode replace \
  --create-if-missing \
  --profile default
```

可选参数：

- `--mode`
- `--create-if-missing`
- `--dry-run`
- `--show`
- `--mutation-key`
- `--audit-dir`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前是对 `manager.block.sync_watchlist(...)` 的薄封装：

- Python task API 使用 `symbols`
- CLI 继续使用可重复 `--stock`
- 底层 `block sync` provider result 原样保留，只额外挂上 task metadata

### 4.5.1 读取自选板块快照

```bash
python -m tdxquant.cli task block-read-watchlist --block-code ZXG --profile default
```

可选参数：

- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前是对 `manager.block.read_watchlist_snapshot(...)` 的薄封装：

- 底层直接调用 `manager.block.read_watchlist_snapshot(...)`
- 返回 provider `data.snapshot` 原样结果

### 4.5.2 导出自选板块快照

```bash
python -m tdxquant.cli task block-read-watchlist-export \
  --block-code ZXG \
  --output runtime/exports/zxg.json \
  --profile default
```

可选参数：

- `--overwrite`
- `--api-profile`
- `--strategy-path`

这个任务当前是对 `manager.block.read_watchlist_snapshot(...)` 的导出型薄封装：

- 先读取 provider `data.snapshot`
- 只把 `data.snapshot` 以单文件 JSON 写到 `--output`
- 返回仍保留 `data.snapshot`，并追加 `data.export`
- `data.export` 当前固定包含：
  - `output_path`
  - `overwritten`
  - `file_size`
- 默认拒绝覆盖已有文件，只有显式 `--overwrite` 才允许替换目标文件
- 同时补齐常规 `data.task` / `data.task_profile` / `data.timing` metadata

### 4.5.3 读取完整板块诊断视图

```bash
python -m tdxquant.cli task block-read-full --block-code ZXG --profile default
```

可选参数：

- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前是对 `manager.block.read_watchlist_snapshot(...)` 的高层 diagnostics 封装：

- 底层仍然只调用一次 `manager.block.read_watchlist_snapshot(...)`
- 继续保留 canonical `data.snapshot`
- 额外追加 task-level `data.read_full`
- `data.read_full` 当前只整理读侧诊断摘要：
  - `sector_name`
  - `raw_member_count`
  - `duplicate_count`
  - `warnings_present`

这里的通用 `--output` 仍然只是：

- 把整条 JSON 结果写到文件

它不是：

- `block-read-watchlist-export` 那条单文件 snapshot 导出语义

如果你已经把固定板块代码收口为 task preset，也可以直接走 preset：

```bash
python -m tdxquant.cli task run --preset read-zxg-watchlist
python -m tdxquant.cli task run --preset read-zxg-watchlist --block-code MYZXG
python -m tdxquant.cli task run --preset read-zxg-full
python -m tdxquant.cli task run --preset read-zxg-full --block-code MYZXG
```

这里的语义保持和其他 `task run --preset ...` 一致：

- `read-zxg-watchlist` 这类 preset 只提供静态 `block_code` 默认值
- `read-zxg-full` 这类 preset 只提供静态 `block_code` 默认值
- 如果命令行显式再传 `--block-code`，以命令行参数为准
- 这仍然只是 `task block-read-full` 的日常命令模板；同一 preset 现在也已经通过 `catalog` entry `read-zxg-full` 暴露
- 当前新增的是 preset-backed catalog 发现与触发，不引入 report / export 打包语义

### 4.6 板块公式扫描

```bash
python -m tdxquant.cli task sector-formula-scan \
  --sector 钛金属 \
  --formula-name MY_FORMULA \
  --profile sector_formula_scan
```

可选参数：

- `--block-type`
- `--list-type`
- `--formula-arg`
- `--return-count`
- `--return-date`
- `--stock-period`
- `--start-time`
- `--end-time`
- `--count`
- `--dividend-type`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务当前会做两步：

1. 调 `manager.meta.sector_stocks(...)` 获取板块成分
2. 提取证券代码后调用 `manager.formula.process_mul_xg(...)`

### 4.6 自选/代码列表导出

```bash
python -m tdxquant.cli task watchlist-export \
  --code 000001 \
  --code 000002 \
  --profile watchlist_export
```

可选参数：

- `--field`
- `--json-output-path`
- `--csv-output-path`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务会：

1. 调 `manager.watchlist_overview(...)`
2. 把完整结果落成 JSON 文件
3. 把行数据落成 CSV 文件

### 4.7 板块研究导出

```bash
python -m tdxquant.cli task sector-research-export \
  --sector 钛金属 \
  --profile sector_research_export
```

可选参数：

- `--block-type`
- `--list-type`
- `--field`
- `--json-output-path`
- `--csv-output-path`
- `--api-profile`
- `--strategy-path`
- `--output`

这个任务会：

1. 调 `manager.sector_research(...)`
2. 把完整结果落成 JSON 文件
3. 把批量行数据落成 CSV 文件

### 4.8 交易买入 Workflow

```bash
python -m tdxquant.cli task trade-buy \
  --port COM3 \
  --code 516820 \
  --price 0.35 \
  --quantity 100 \
  --profile trade_buy
```

可选参数：

- `--refresh-before-trade`
- `--refresh-market`
- `--refresh-force`
- `--trade-profile`
- `--output`

这个任务当前会：

1. 可选调用 `manager.api_manager.refresh_cache(...)`
2. 调 `manager.trade_manager.pingan.buy(...)`
3. 返回统一 task 结果，并保留 trade 产物路径

### 4.9 交易 Submit Once Workflow

```bash
python -m tdxquant.cli task trade-submit-once \
  --port COM3 \
  --code 516820 \
  --price 0.35 \
  --quantity 100 \
  --profile trade_submit_once
```

可选参数：

- `--refresh-before-trade`
- `--refresh-market`
- `--refresh-force`
- `--trade-profile`
- `--output`

这个任务当前会：

1. 可选调用 `manager.api_manager.refresh_cache(...)`
2. 调 `manager.trade_manager.pingan.buy_submit_once(...)`
3. 返回统一 task 结果，并保留 trade 产物路径

### 4.10 受保护买入 Workflow

```bash
python -m tdxquant.cli task guarded-trade-buy \
  --port COM3 \
  --code 516820 \
  --price 0.35 \
  --quantity 100 \
  --max-snapshot-price 0.36 \
  --required-block-code ZXG \
  --profile guarded_trade_buy
```

可选参数：

- `--refresh-before-trade`
- `--refresh-market`
- `--refresh-force`
- `--max-snapshot-price`
- `--required-block-code`
- `--required-block-type`
- `--required-list-type`
- `--formula-name`
- `--formula-arg`
- `--formula-return-count`
- `--formula-return-date`
- `--formula-stock-period`
- `--formula-start-time`
- `--formula-end-time`
- `--formula-count`
- `--formula-dividend-type`
- `--json-output-path`
- `--csv-output-path`
- `--trade-profile`
- `--output`

这个任务当前会：

1. 可选先刷新环境
2. 如果提供 `--max-snapshot-price`，先调 `manager.market.snapshot(...)` 检查当前价
3. 如果提供 `--required-block-code`，先调 `manager.meta.sector_stocks(...)` 检查标的是否属于目标板块
4. 如果提供 `--formula-name`，先调 `manager.formula_scan(...)` 检查目标证券是否命中公式
5. 前置检查通过后再调 `manager.trade_buy(...)`
6. 额外生成一份 JSON 报告和一份 CSV 摘要
7. 同时追加一份 JSONL/CSV 连续台账，方便追踪历史执行记录

### 4.11 台账汇总 Workflow

```bash
python -m tdxquant.cli task ledger-summary \
  --code 516820 \
  --trade-ok \
  --profile ledger_summary
```

可选参数：

- `--limit`
- `--code`
- `--contract-no`
- `--trade-ok` / `--no-trade-ok`
- `--task-name`
- `--ledger-jsonl-path`
- `--ledger-csv-path`
- `--json-output-path`
- `--csv-output-path`
- `--output`

这个任务当前会：

1. 优先读取默认或显式指定的 JSONL 台账
2. 如果 JSONL 不存在，则回退读取 CSV 台账
3. 按 `code` / `contract_no` / `task_name` / `trade_ok` 做过滤
4. 返回总记录数、命中数、成功数、失败数、最近时间戳等摘要
5. 返回最近若干条记录
6. 如果提供导出参数，则把当前筛选视图导出为 JSON/CSV

### 4.12 日内交易报表 Workflow

```bash
python -m tdxquant.cli task daily-trade-report \
  --date 2026-04-26 \
  --profile daily_trade_report
```

可选参数：

- `--date`
- `--timezone`
- `--recent-limit`
- `--code`
- `--trade-ok` / `--no-trade-ok`
- `--task-name`
- `--ledger-jsonl-path`
- `--ledger-csv-path`
- `--json-output-path`
- `--csv-output-path`
- `--output`

这个任务当前会：

1. 读取默认或显式指定的 ledger 文件
2. 先按 `code` / `trade_ok` / `task_name` 做基础过滤
3. 再按指定时区下的本地交易日做日期过滤
4. 输出当日记录总数、成功/失败数、总数量、名义总金额
5. 输出按代码聚合的汇总结果
6. 输出最近若干条当日记录
7. 如果提供导出参数，则写出 JSON 完整报表和 CSV 按代码聚合表

### 4.13 单次交易报告回溯 Workflow

```bash
python -m tdxquant.cli task trade-report-lookup \
  --contract-no B202604260301 \
  --profile trade_report_lookup
```

也可以按代码查候选：

```bash
python -m tdxquant.cli task trade-report-lookup \
  --code 516820 \
  --date 2026-04-26 \
  --profile trade_report_lookup
```

可选参数：

- `--contract-no`
- `--code`
- `--date`
- `--timezone`
- `--limit`
- `--trade-ok` / `--no-trade-ok`
- `--task-name`
- `--ledger-jsonl-path`
- `--ledger-csv-path`
- `--json-output-path`
- `--csv-output-path`
- `--output`

这个任务当前会：

1. 读取默认或显式指定的 ledger 文件
2. 按 `contract_no` 或 `code` 做主过滤
3. 可选结合本地交易日、`trade_ok`、`task_name` 继续收窄结果
4. 返回匹配 ledger 条目和关联的 `report_json_path` / `report_csv_path`
5. 同时给出报告文件是否仍然存在
6. 如果唯一命中且 JSON 报告存在，则直接加载报告内容
7. 如果提供导出参数，则写出 JSON 查找结果和 CSV 候选表

### 4.14 区间交易报表 Workflow

```bash
python -m tdxquant.cli task trade-period-report \
  --start-date 2026-04-20 \
  --end-date 2026-04-26 \
  --profile trade_period_report
```

只给单边日期也可以，另一边会自动补齐成同一天：

```bash
python -m tdxquant.cli task trade-period-report \
  --start-date 2026-04-26 \
  --profile trade_period_report
```

可选参数：

- `--start-date`
- `--end-date`
- `--timezone`
- `--recent-limit`
- `--code`
- `--trade-ok` / `--no-trade-ok`
- `--task-name`
- `--ledger-jsonl-path`
- `--ledger-csv-path`
- `--json-output-path`
- `--csv-output-path`
- `--output`

这个任务当前会：

1. 读取默认或显式指定的 ledger 文件
2. 先按 `code` / `trade_ok` / `task_name` 做基础过滤
3. 再按本地日期区间 `[start_date, end_date]` 做 inclusive 过滤
4. 输出区间总记录数、交易日数量、成功/失败数、总数量、名义总金额
5. 输出 `by_day` 和 `by_code` 两层聚合结果
6. 输出最近若干条区间内记录
7. 如果提供导出参数，则写出 JSON 完整报表和 CSV 按日聚合表

## 5. 输出结构

task 层返回的结果在原有 `Result` 基础上新增：

- `data.task`
  - `entrypoint`
  - `name`
- `data.task_profile`
  - `name`
  - `options`
- `data.timing.task_call`

这意味着 task 输出会同时保留：

- task 维度元数据
- task 内部 manager 调用产物
- 原有标准 `ok/code/message/warnings/next_action`

## 6. 当前限制

- `sector-research` 依赖 `sector_stocks` 返回中能提取出证券代码；如果返回结构变化，需要调整抽取规则。
- `formula-scan` 当前只编排批量选股公式路径，没有自动做公式数据准备。
- `watchlist-overview` 本质上仍是 `gp_one_data` 的场景化封装，字段质量依赖底层数据源。
- `sector-formula-scan` 依赖板块成分结果里能稳定提取出证券代码。
- 导出类 task 的 CSV 目前采用通用行格式，复杂嵌套结构不会自动做精细报表化。
- task 层暂不混入桌面自动化交易流程。

## 7. 推荐用法

推荐把使用方式分成两层：

- 原子验证、调试、精细控制：优先 `api`
- 日常固定流程：优先 `task`

也就是：

- `api` 是底层稳定门面
- `task` 是日常使用门面

后续如果继续扩展，优先增加新的稳定 task，而不是继续在 shell 里手写长命令拼装流程。

## 8. Report 快捷组

针对已经稳定下来的报表类 task，CLI 现在还提供一组更短的 `report` 入口：

- `report ledger`
- `report daily`
- `report period`
- `report lookup`

这些命令本质上仍然复用 `TdxTaskManager` 的报表类 workflow，只是：

- 子命令更短
- 默认 profile 已经绑定到对应报表能力

示例：

```bash
python -m tdxquant.cli report daily --date 2026-04-26
python -m tdxquant.cli report period --start-date 2026-04-20 --end-date 2026-04-26
python -m tdxquant.cli report lookup --contract-no B202604260301
python -m tdxquant.cli report ledger --code 516820 --trade-ok
```

如果你是日常复盘或排障，优先用 `report`。
如果你是在搭更复杂的组合流程，仍然优先用 `task`。

## 9. Report Presets

如果你已经把常用报表参数固化为 runtime preset，可以直接使用：

```bash
python -m tdxquant.cli report presets
python -m tdxquant.cli report run --preset daily-review
python -m tdxquant.cli report run --preset daily-success --date 2026-04-26
python -m tdxquant.cli report run --preset period-review --start-date 2026-04-20 --end-date 2026-04-26
```

边界约定：

- `report presets` 用于查看当前可用 preset 列表。
- `report run --preset ...` 只是一层 CLI alias，最终仍然走既有 `report ledger|daily|lookup|period` workflow。
- preset 中定义的是默认参数；如果命令行显式再传一次同名参数，以命令行参数为准。
- preset 与 `task profile` 不同：前者面向“更短的日常命令”，后者面向“底层 workflow 默认值”。

## 10. Task Presets

如果你已经把高频 task workflow 的环境参数固定下来，可以直接使用 task preset：

```bash
python -m tdxquant.cli task presets
python -m tdxquant.cli task run --preset refresh-default
python -m tdxquant.cli task run --preset guarded-default --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli task run --preset task-buy-default --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli task run --preset submit-once-default --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli task run --preset submit-ready-default --code 516820 --price 0.35 --quantity 100
python -m tdxquant.cli task run --preset confirm-current-default
python -m tdxquant.cli task run --preset read-zxg-watchlist
python -m tdxquant.cli task run --preset read-zxg-watchlist --block-code MYZXG
python -m tdxquant.cli task run --preset read-zxg-full
python -m tdxquant.cli task run --preset read-zxg-full --block-code MYZXG
```

当前 `task preset` 稳定覆盖：

- `refresh-environment`
- `trade-buy`
- `trade-submit-once`
- `trade-submit-ready`
- `trade-confirm-current`
- `guarded-trade-buy`
- `block-read-watchlist`
- `block-read-watchlist-export`
- `block-read-full`

边界约定：

- `task preset` 只是一层 CLI alias，最终仍然走既有稳定 `task` workflow。
- preset 中定义的是命令级默认参数；如果命令行显式再传一次同名参数，以命令行参数为准。
- `task profile` 负责 workflow 默认行为，`task preset` 负责日常命令模板。
- `block-read-watchlist` 当前已支持这种静态 preset 打包；它仍然只是标准化 snapshot 读取入口，不引入 catalog / report / export 语义。
- `block-read-full` 当前已支持这种静态 preset 打包，并通过同名 preset-backed catalog entry 暴露；仍不包含 report / export 打包。
- `report` 类查询 workflow 已经有独立的 `report preset`，不建议再通过 `task preset` 重复配置。
