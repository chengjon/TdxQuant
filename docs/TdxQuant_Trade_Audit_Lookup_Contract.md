# TdxQuant Trade Audit Lookup Contract

本文定义稳定 `trade_audit` 消费入口的当前 contract。

它关注的是：

- 如何稳定读取 `runtime/trade-audits/` 中的不可变审计文件
- `task` / `report` 两层入口如何暴露审计 lookup
- 唯一命中与候选列表的返回语义

它不关注：

- `trade_audit` 文件是如何写出来的
- 按日或按区间的审计聚合细节
- catalog / bundle 层的日常收口

## 1. 当前入口

当前稳定入口包括：

- Python：
  - `TdxTaskManager.trade_audit_lookup(...)`
- CLI：
  - `tdxquant task trade-audit-lookup ...`
  - `tdxquant report audit-lookup ...`

其中 `report audit-lookup` 是 `task` 工作流的稳定 report 别名，不维护独立逻辑。

## 2. 当前目标

这一版 lookup contract 解决 3 件事：

- 按 `audit_id` 精确定位单条审计记录
- 按 `contract_no`、`submission_key`、`code` 查看候选记录
- 在唯一命中时直接返回完整审计 JSON

## 3. 默认数据源

默认审计目录：

- `runtime/trade-audits/`

当前支持显式覆盖：

- `--audit-dir`

当前 lookup 只读取不可变审计 JSON artifact，不依赖：

- `last_order_state`
- `order_event_log`
- `submission_ledger`

## 4. 输入参数

当前支持：

- `audit_id`
- `contract_no`
- `submission_key`
- `code`
- `status`
- `limit`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

其中主查询键至少需要一个：

- `audit_id`
- `contract_no`
- `submission_key`
- `code`

`status` 只能作为附加过滤条件。

## 5. 结果结构

当前返回的 `data` 至少包含：

- `input`
- `source`
- `summary`
- `entries`
- `audit`
- `artifacts`

其中：

- `entries` 总是轻量摘要视图
- `audit` 只在唯一命中时出现
- `artifacts` 只在导出时出现

## 6. Entry Summary View

每条 `entries` 当前固定摘要字段包括：

- `audit_id`
- `recorded_at`
- `status`
- `method`
- `broker`
- `code`
- `contract_no`
- `submission_key`
- `side_effect_level`
- `audit_path`

候选列表当前按 `recorded_at` 从新到旧排序。

## 7. Unique Match Rules

当前当且仅当过滤后结果数为 `1` 时：

- `summary.unique_match = true`
- `summary.loaded_audit = true`
- 返回完整 `audit` payload

如果命中多条：

- `summary.unique_match = false`
- 只返回 `entries`

## 8. 导出

当前支持导出：

- JSON summary
- CSV candidate rows

默认 export stem：

- `trade-audit-lookup`

## 9. 当前边界

这一版还没有提供：

- `trade_audit` 聚合 workflow 的 contract 细节
- 基于 catalog/preset 的默认日常入口
- 审计目录索引缓存
- 跨 `trade_audit` / task ledger / submission ledger 的组合查询
