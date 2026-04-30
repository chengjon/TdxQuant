## Why

当前 task 层已经有单日汇总和单次报告回溯，但还缺少一个稳定的“日期范围报表”入口。日常复盘时，用户往往需要看一段时间内的整体执行情况，例如最近一周、最近一月总共成交了多少笔、哪几天活跃、哪些代码累计最多。

现在需要把这个区间聚合能力也收进 task 层，避免继续手工拼接多天日报。

## What Changes

- 为 task 层增加 `trade_period_report` workflow。
- 支持按 `start_date` / `end_date` 和时区过滤 ledger 记录。
- 支持输出按日期聚合与按代码聚合的区间统计结果。
- 为 CLI 增加 `task trade-period-report` 入口，并支持可选 JSON/CSV 导出。

## Capabilities

### New Capabilities

- `tdx-task-trade-period-report`: 提供基于连续台账的日期范围交易汇总能力

### Modified Capabilities

- `tdx-task-management`: task 管理层新增稳定的区间交易报表 workflow

## Impact

- 影响 `tdxquant/api/task.py`、`tdxquant/cli.py`、`runtime/task-profiles.json`、任务层文档与测试。
- 让报表层从“单日”扩展到“日期范围”，但仍然保持和单次回溯能力解耦。
