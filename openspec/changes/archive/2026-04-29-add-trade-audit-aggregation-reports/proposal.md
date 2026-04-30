## Why

`trade_audit` 现在已经有稳定 lookup 入口，但仍然缺少按日和按区间的聚合消费能力。调用方如果想看某一天或一段时间内的交易审计概况，仍然需要自行遍历 `runtime/trade-audits/` 目录，不利于日常复盘和后续 report 收口。

当前最自然的下一步是补两条稳定 workflow：

- day-level aggregation
- range-level aggregation

这样 `trade_audit` 才能从“单条可查”进入“日常可复盘”的状态。

## What Changes

- 新增稳定 task workflow：
  - `TdxTaskManager.trade_audit_daily_report(...)`
  - `TdxTaskManager.trade_audit_period_report(...)`
- 新增 CLI：
  - `task trade-audit-daily-report`
  - `task trade-audit-period-report`
  - `report audit-daily`
  - `report audit-period`
- 新增 task/report 默认 profile 映射：
  - `trade_audit_daily_report`
  - `trade_audit_period_report`
- 提供基于 `runtime/trade-audits/` 的本地日期聚合、按区间聚合和导出

## Impact

- 新增 specs：
  - `tdx-task-trade-audit-daily-report`
  - `tdx-task-trade-audit-period-report`
- 更新 specs：
  - `tdx-task-management`
  - `tdx-report-cli-entry`
- 代码影响集中在：
  - `tdxquant/api/task.py`
  - `tdxquant/cli.py`
  - `tdxquant/tasking.py`
  - `tdxquant/reporting.py`
  - `runtime/task-profiles.json`
