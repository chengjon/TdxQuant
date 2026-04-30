## Why

现在 task 层已经能生成连续 ledger，也能做摘要和日报，但还缺少一个“从某次交易直接回到单次报告文件”的稳定入口。日常排障时，最常见的问题往往不是看统计，而是拿到一个合同号或代码后，快速定位那一单对应的 JSON/CSV 报告和前置检查结果。

现在需要把这条回溯链也收进 task 层，避免继续手工翻 ledger 文件和路径字段。

## What Changes

- 为 task 层增加 `trade_report_lookup` workflow。
- 支持按 `contract_no` 精确回溯单次任务报告。
- 支持按 `code` 辅助查询候选记录，并可结合日期/任务名过滤。
- 支持在唯一命中时直接加载单次 JSON 报告内容。
- 为 CLI 增加 `task trade-report-lookup` 入口，并支持可选 JSON/CSV 导出。

## Capabilities

### New Capabilities

- `tdx-task-trade-report-lookup`: 提供基于连续台账回溯单次交易报告的稳定 workflow

### Modified Capabilities

- `tdx-task-management`: task 管理层新增稳定的交易报告回溯 workflow

## Impact

- 影响 `tdxquant/api/task.py`、`tdxquant/cli.py`、`runtime/task-profiles.json`、任务层文档与测试。
- 让 task 层从“能生成报告”和“能看汇总”继续扩展到“能定位单次报告”。
