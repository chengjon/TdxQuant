## Context

当前报表链路已经覆盖：

- `ledger_summary`: 原始记录筛选
- `daily_trade_report`: 单日聚合
- `trade_report_lookup`: 单次报告回溯

但一旦需要跨多日观察趋势，用户仍然要自己多次调用 `daily_trade_report` 后再合并结果。这种方式不适合作为稳定的日常入口。

## Goals / Non-Goals

**Goals:**

- 提供稳定的 `trade_period_report` task。
- 支持基于本地日期边界做区间过滤。
- 输出区间总览、按日聚合、按代码聚合和最近记录。
- 支持导出 JSON 全量报表和 CSV 按日聚合视图。

**Non-Goals:**

- 不取代 `daily_trade_report` 的单日职责。
- 不做更复杂的 BI、图表或数据库模型。
- 不修改 ledger 结构和交易执行路径。

## Decisions

### 1. `start_date` / `end_date` 显式建模，单边默认补齐

如果只提供 `start_date` 或 `end_date`，另一端自动补成同一天。这样既能表达单日，也能自然扩展到日期范围，同时避免“默认最近 7 天”这类隐式行为。

### 2. JSON 保留全量结构，CSV 先专注按日汇总

区间报表天然有多种聚合维度。首版 JSON 返回：

- summary
- by_day
- by_code
- entries

CSV 则先输出 `by_day`，优先满足最常见的时间序列复盘需求。

### 3. 继续复用 ledger 过滤和金额聚合 helper

本次不重新实现数据准备逻辑，而是复用现有的：

- ledger source 读取
- 通用字段过滤
- 本地日期提取
- 按代码聚合

只新增区间日期过滤和按日聚合 helper。

## Risks / Trade-offs

- [区间过大导致结果较大] → 保留 `recent_limit` 控制明细返回规模，聚合结果仍保持紧凑。
- [CSV 只导出按日，不含按代码] → 按代码信息继续保留在 JSON，后续如有需要再补导出维度参数。
- [日期参数误用] → 对非法日期格式和 `start_date > end_date` 明确返回 `INVALID_REQUEST`。
