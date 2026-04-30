## Why

`guarded_trade_buy` 已经会持续追加 JSONL/CSV 台账，但目前缺少一个稳定的 task 入口来消费这些历史记录。日常使用时如果还要手工翻文件、自己统计最近成功单和合同号，task 层就还没有形成闭环。

现在需要补一个面向台账消费的稳定 workflow，让调用方可以直接查看最近记录、按条件筛选，并导出筛选结果。

## What Changes

- 为 task 层增加 `ledger_summary` 能力，用于读取连续台账并返回稳定摘要。
- 为 CLI 增加 `task ledger-summary` 子命令。
- 支持按 `code`、`contract_no`、`trade_ok`、`task_name` 过滤。
- 支持返回最近若干条记录，并可选导出当前筛选结果为 JSON/CSV。

## Capabilities

### New Capabilities

- `tdx-task-ledger-summary`: 提供连续任务台账的读取、筛选、摘要和导出能力

### Modified Capabilities

- `tdx-task-management`: task 管理层新增稳定的 ledger summary workflow 入口

## Impact

- 影响 `tdxquant/api/task.py`、`tdxquant/cli.py`、`runtime/task-profiles.json`、任务层文档与测试。
- 让 `guarded_trade_buy` 生成的 ledger 能被后续任务直接消费，而不是停留在原始文件级别。
