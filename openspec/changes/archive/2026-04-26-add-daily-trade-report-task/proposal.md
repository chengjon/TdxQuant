## Why

现在 task 层已经能持续生成和读取 ledger，但日常使用里仍然缺少一个“直接看当日交易结果”的稳定入口。调用方如果想快速知道某一天做了几笔、哪些代码成功、总下单数量和金额概况，仍然需要自己再做一层统计。

现在需要把这层日常汇总也收进 task 层，形成从交易执行、台账沉淀到日报查看的完整闭环。

## What Changes

- 为 task 层增加 `daily_trade_report` workflow。
- 支持基于 ledger 按交易日生成聚合摘要。
- 支持输出按代码聚合的日内汇总结果。
- 为 CLI 增加 `task daily-trade-report` 入口，并支持可选 JSON/CSV 导出。

## Capabilities

### New Capabilities

- `tdx-task-daily-trade-report`: 提供基于连续台账的日内交易汇总能力

### Modified Capabilities

- `tdx-task-management`: task 管理层新增稳定的日内交易报表 workflow

## Impact

- 影响 `tdxquant/api/task.py`、`tdxquant/cli.py`、`runtime/task-profiles.json`、任务层文档与测试。
- 让 ledger 不仅能被逐条查询，也能直接形成按交易日聚合的稳定结果。
