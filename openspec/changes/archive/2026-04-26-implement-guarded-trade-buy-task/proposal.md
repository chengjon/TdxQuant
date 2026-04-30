## Why

当前 task 层已经可以编排：

- 查询 API
- 桌面交易执行

但还缺少一个更完整的“交易任务模板”，无法把常见的买入前保护逻辑一起收口。例如：

- 先看当前价是否满足上限
- 先确认标的是否属于指定板块
- 条件通过后才执行交易
- 同时落一份完整任务报告

现在需要先实现一个最小可用的“受保护买入 task”，把常见前置检查、交易执行和报告产物合在一个稳定入口里。

## What Changes

- 为 `TdxTaskManager` 增加 `guarded_trade_buy`。
- 新增 CLI：
  - `task guarded-trade-buy`
- 支持前置检查：
  - snapshot 当前价上限
  - required block 成分归属
- 为该 task 生成 JSON/CSV 报告产物。

## Capabilities

### Modified Capabilities

- `tdx-task-management`

## Impact

- task 层具备第一个“条件检查 + 交易执行 + 任务报告”的完整模板。
- 为后续继续扩展 formula/snapshot/sector 等更复杂的交易前置判断提供基础结构。
