## Why

当前项目已经具备三层能力：

- `TdxApiManager` 负责查询与只读 API
- `TdxTradeManager` 负责桌面交易稳定执行
- `trade` CLI 负责稳定交易顶层命令入口

但日常使用仍然缺少一个更高层的稳定 workflow 入口，无法把：

- 环境刷新
- 交易执行
- 结果与产物回填

编排为一个场景化 task。既然 task 层已经是日常高频调用的统一入口，就应该开始纳入桌面交易 workflow。

## What Changes

- 为 `TdxTaskManager` 引入 `TdxTradeManager` 依赖。
- 新增交易 task：
  - `trade_buy`
  - `trade_submit_once`
- 支持 task 级可选环境刷新，然后再执行桌面交易。
- 在 CLI 中新增：
  - `task trade-buy`
  - `task trade-submit-once`
- 补充 profile、文档与测试。

## Capabilities

### Modified Capabilities

- `tdx-task-management`

## Impact

- task 层从“只编排 API”扩展为“可编排 API + Trade”。
- 日常调用开始有统一的交易 workflow 入口。
- 为后续继续做“行情判断 + 交易执行 + 导出/回填”的更复杂任务打下基础。
