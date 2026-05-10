# TdxQuant Trade Audit Report Contract

本文定义稳定 `trade_audit` 聚合消费入口的当前 contract。

它关注的是：

- 如何按日消费 `runtime/trade-audits/`
- 如何按区间消费 `runtime/trade-audits/`
- `task` / `report` 两层入口如何暴露聚合 workflow

它不关注：

- `trade_audit` 文件的写入逻辑
- 单条审计的精确 lookup 语义
- 更复杂的 catalog / preset 组合扩展

## 1. 当前入口

当前稳定入口包括：

- Python：
  - `TdxTaskManager.trade_audit_daily_report(...)`
  - `TdxTaskManager.trade_audit_period_report(...)`
- CLI：
  - `tdxquant task trade-audit-daily-report ...`
  - `tdxquant task trade-audit-period-report ...`
  - `tdxquant report audit-daily ...`
  - `tdxquant report audit-period ...`

其中 `report audit-daily` 与 `report audit-period` 都是 `task` 工作流的稳定 report 别名。

当前已配套的日常入口配置包括：

- report presets：
  - `audit-daily-review`
  - `audit-daily-confirmed`
  - `audit-daily-rejected`
  - `audit-daily-replayed`
  - `audit-daily-failed`
  - `audit-daily-exceptions`
  - `audit-daily-confirm-exceptions`
  - `audit-daily-pingan-confirm-exceptions`
  - `audit-daily-submit-once-exceptions`
  - `audit-daily-pingan-submit-once-exceptions`
  - `audit-daily-buy-exceptions`
  - `audit-daily-sell-exceptions`
  - `audit-daily-submit-path-exceptions`
  - `audit-daily-pingan-submit-path-exceptions`
  - `audit-daily-pingan-order-exceptions`
  - `audit-period-review`
  - `audit-period-confirmed`
  - `audit-period-rejected`
  - `audit-period-replayed`
  - `audit-period-failed`
  - `audit-period-exceptions`
  - `audit-period-confirm-exceptions`
  - `audit-period-pingan-confirm-exceptions`
  - `audit-period-submit-once-exceptions`
  - `audit-period-pingan-submit-once-exceptions`
  - `audit-period-buy-exceptions`
  - `audit-period-sell-exceptions`
  - `audit-period-submit-path-exceptions`
  - `audit-period-pingan-submit-path-exceptions`
  - `audit-period-pingan-order-exceptions`
- catalog entries：
  - `audit-daily-review`
  - `audit-daily-confirmed`
  - `audit-daily-rejected`
  - `audit-daily-replayed`
  - `audit-daily-failed`
  - `audit-daily-exceptions`
  - `audit-daily-confirm-exceptions`
  - `audit-daily-pingan-confirm-exceptions`
  - `audit-daily-submit-once-exceptions`
  - `audit-daily-pingan-submit-once-exceptions`
  - `audit-daily-buy-exceptions`
  - `audit-daily-sell-exceptions`
  - `audit-daily-submit-path-exceptions`
  - `audit-daily-pingan-submit-path-exceptions`
  - `audit-daily-pingan-order-exceptions`
  - `audit-period-review`
  - `audit-period-confirmed`
  - `audit-period-rejected`
  - `audit-period-replayed`
  - `audit-period-failed`
  - `audit-period-exceptions`
  - `audit-period-confirm-exceptions`
  - `audit-period-pingan-confirm-exceptions`
  - `audit-period-submit-once-exceptions`
  - `audit-period-pingan-submit-once-exceptions`
  - `audit-period-buy-exceptions`
  - `audit-period-sell-exceptions`
  - `audit-period-submit-path-exceptions`
  - `audit-period-pingan-submit-path-exceptions`
  - `audit-period-pingan-order-exceptions`
- diagnostic / follow-up bundles：
  - `audit-diagnostics`
  - `audit-rejection-diagnostics`
  - `audit-confirmed-review`
  - `audit-replay-review`
  - `audit-failure-diagnostics`
  - `audit-exception-diagnostics`
  - `audit-confirm-exception-diagnostics`
  - `audit-pingan-confirm-exception-diagnostics`
  - `audit-submit-once-exception-diagnostics`
  - `audit-pingan-submit-once-exception-diagnostics`
  - `audit-buy-exception-diagnostics`
  - `audit-sell-exception-diagnostics`
  - `audit-submit-path-exception-diagnostics`
  - `audit-pingan-submit-path-exception-diagnostics`
  - `audit-pingan-order-exception-diagnostics`
  - `submit-ready-audit-review`
  - `submit-ready-exception-review`
  - `confirm-audit-review`
  - `confirm-complete-review`
  - `confirm-exception-review`
  - `confirm-pingan-exception-review`
  - `submit-once-exception-review`
  - `submit-once-pingan-exception-review`
  - `guarded-buy-exception-review`
  - `confirm-submit-path-exception-review`
  - `confirm-pingan-submit-path-exception-review`

## 2. 当前目标

这一版聚合 contract 解决 2 件事：

- 提供单日审计聚合视图
- 提供闭区间审计聚合视图

## 3. 默认数据源

默认审计目录：

- `runtime/trade-audits/`

当前支持显式覆盖：

- `--audit-dir`

当前聚合 workflow 只读取不可变审计 JSON artifact，不依赖：

- `last_order_state`
- `order_event_log`
- `submission_ledger`

## 4. Daily Report

当前 daily report 支持：

- `date`
- `timezone`
- `recent_limit`
- `code`
- `status`
- `statuses`
- `method`
- `methods`
- `broker`
- `submission_key`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

CLI 层额外支持：

- `--status`
- `--status-any ...`（可重复，用于 OR 过滤）
- `--method`
- `--method-any ...`（可重复，用于 OR 过滤）

约束：

- `status` 与 `statuses` 不能同时使用
- `method` 与 `methods` 不能同时使用

当前结果结构至少包括：

- `input`
- `source`
- `summary`
- `by_code`
- `by_status`
- `entries`
- `artifacts`

## 5. Period Report

当前 period report 支持：

- `start_date`
- `end_date`
- `timezone`
- `recent_limit`
- `code`
- `status`
- `statuses`
- `method`
- `methods`
- `broker`
- `submission_key`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

CLI 层额外支持：

- `--status`
- `--status-any ...`（可重复，用于 OR 过滤）
- `--method`
- `--method-any ...`（可重复，用于 OR 过滤）

约束：

- `status` 与 `statuses` 不能同时使用
- `method` 与 `methods` 不能同时使用

当前结果结构至少包括：

- `input`
- `source`
- `summary`
- `by_day`
- `by_code`
- `by_status`
- `entries`
- `artifacts`

## 6. Current Aggregation Semantics

当前 daily / period 聚合以“审计治理视角”为主，重点输出：

- entries count
- status counts
- unique codes
- unique contracts
- latest recorded timestamp

当前不做：

- 价格聚合
- 数量聚合
- 金额聚合

## 7. Current Limits

这一版已经提供：

- 单方法 `method`
- 多方法 `methods` OR 过滤
- 第一组 submit path 组合视角：`buy_submit_once + confirm_current`
- 第一组 broker-scoped confirm 组合视角：`pingan + confirm_current + rejected|failed`
- 第一组 broker-scoped submit-once 组合视角：`pingan + buy_submit_once + rejected|failed`
- 第一组 broker-scoped submit path 组合视角：`pingan + buy_submit_once + confirm_current + rejected|failed`

这一版还没有提供：

- 更高阶的 broker / method / status 多维 audit diagnostics 组合矩阵
- 审计目录索引缓存
- 跨 `trade_audit` / task ledger / submission ledger 的组合聚合
