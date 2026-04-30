## Overview

本 change 为稳定桌面交易审计产物补一个 lookup-only 工作流，不做日报、期间聚合或 catalog 扩展。

目标是让调用方不用直接解析 `runtime/trade-audits/*.json`，而是通过稳定 `task` / `report` 入口完成：

- 精确 lookup：`audit_id`
- 候选 lookup：`contract_no`、`submission_key`、`code`
- 辅助过滤：`status`
- 唯一命中时返回完整审计 JSON

## Design Decisions

### 1. 先做 lookup，不做聚合

`trade_audit` 的当前缺口是“单条审计可稳定消费”，不是“多日汇总”。如果把 lookup 和 rollup 混在一包里，会把输出 contract、筛选语义和 CLI 子命令一起拉大。

因此本包只提供：

- `trade_audit_lookup`
- 候选列表
- 唯一命中完整载入
- 导出

日报、期间汇总和 catalog 入口留到后续 change。

### 2. 复用现有 report/task 风格

当前项目已经有稳定模式：

- `task trade-report-lookup`
- `report lookup`

本包沿用这类 contract 和 dispatch 方式，但避免覆盖现有 `report lookup` 语义，因此新增显式子命令：

- `task trade-audit-lookup`
- `report audit-lookup`

### 3. 目录扫描以审计目录为唯一数据源

工作流只读取 `trade_audit` JSON artifact，不再依赖 task ledger、submission ledger 或 last-order state。

默认目录：

- `runtime/trade-audits/`

支持显式覆盖：

- `--audit-dir`

### 4. 唯一命中才回填完整审计 payload

为了避免候选列表响应过重：

- `entries` 只返回轻量摘要视图
- 只有唯一命中时才返回 `audit`

这和现有 `trade_report_lookup` 在唯一命中时加载完整 report 的模式一致。

## Workflow Shape

### Input

- `audit_id`
- `contract_no`
- `submission_key`
- `code`
- `status`
- `limit`
- `audit_dir`
- `json_output_path`
- `csv_output_path`

至少需要一个主查询键：

- `audit_id`
- `contract_no`
- `submission_key`
- `code`

`status` 只能作为附加过滤器。

### Output

主结果结构包含：

- `input`
- `source`
- `summary`
- `entries`
- `audit`（仅唯一命中时）
- `artifacts`（导出时）

每条 `entries` 摘要包含：

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

## Risks

### 损坏或非预期 JSON

审计目录可能混入损坏文件或非标准文件。工作流不应整体失败，而应：

- 跳过损坏文件
- 在 `warnings` 中记录失败文件

### 宽查询返回过大

如果只按 `code` 查询，可能命中多条。为控制返回规模，继续提供：

- `limit`
- newest-first 排序

## Out of Scope

- 按日期聚合 trade audit
- trade audit 日报 / 周报
- report preset 或 catalog 默认项
- 交叉关联 task ledger / submission ledger 聚合分析
