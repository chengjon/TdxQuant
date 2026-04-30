## Overview

本 change 为 `trade_audit` 补两个稳定聚合 workflow：

- `trade_audit_daily_report`
- `trade_audit_period_report`

两者都只读取不可变审计目录，不依赖 state、event 或 submission ledger。

## Design Decisions

### 1. daily 与 period 同包实现

这两条 workflow 共用：

- 审计目录扫描
- 本地日期提取
- 基础过滤
- 聚合 helper
- `task` / `report` 分发模式

拆成两个 change 会重复大量样板，因此放在一个小包里更合理。

### 2. 继续把 `report` 作为 `task` 的稳定别名

和现有 `daily / period / lookup` 一样：

- `task trade-audit-daily-report`
- `task trade-audit-period-report`
- `report audit-daily`
- `report audit-period`

共享同一套 `TdxTaskManager` 实现，不引入独立 report 逻辑。

### 3. 聚合字段以“审计治理视角”为主

`trade_audit` 没有稳定的价格、数量、金额字段，因此这一版不做金额聚合，而是聚合：

- entries count
- status counts
- unique codes
- unique contracts
- latest timestamp

必要时再补更细的业务指标。

### 4. 基础过滤保持保守

这一版支持的主要过滤器：

- `code`
- `status`
- `method`
- `broker`
- `submission_key`

不把 lookup 语义和聚合语义混在一起，因此：

- `audit_id`
- `contract_no`

仍然优先留给 lookup workflow。

## Workflow Shape

### trade_audit_daily_report

输入：

- `report_date`
- `timezone_name`
- `recent_limit`
- `code`
- `status`
- `method`
- `broker`
- `submission_key`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

输出：

- `input`
- `source`
- `summary`
- `by_code`
- `by_status`
- `entries`
- `artifacts`

### trade_audit_period_report

输入：

- `start_date`
- `end_date`
- `timezone_name`
- `recent_limit`
- `code`
- `status`
- `method`
- `broker`
- `submission_key`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

输出：

- `input`
- `source`
- `summary`
- `by_day`
- `by_code`
- `by_status`
- `entries`
- `artifacts`

## Aggregation Rules

### Daily

- 默认使用配置 timezone 的当前本地日期
- `entries` 返回最近若干条命中审计
- `by_code` 提供按股票代码聚合
- `by_status` 提供按状态聚合

### Period

- 只给一个边界时，当作单日区间
- 双边界时按闭区间过滤
- `by_day` 按本地日期聚合
- `by_code` 与 `by_status` 提供横向统计

## Out of Scope

- report preset 默认项
- catalog 默认入口
- 基于金额/数量的成交统计
- 跨 ledger/state/event 的联表复盘
