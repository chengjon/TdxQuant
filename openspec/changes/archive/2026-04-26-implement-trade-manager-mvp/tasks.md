## 1. Trade Manager Package

- [x] 1.1 新增 `tdxquant/trade/` 包，并提供 `TdxTradeManager` 与平安 broker 代理。
- [x] 1.2 新增桌面交易 profile/context 辅助层，统一 profile 解析、metadata、状态文件与事件日志写入。

## 2. CLI Integration

- [x] 2.1 将 `pingan-buy` 切换为通过 `TdxTradeManager` 执行，同时保持原参数兼容。
- [x] 2.2 将 `pingan-buy-submit-once` 切换为通过 `TdxTradeManager` 执行，同时保持原参数兼容。
- [x] 2.3 保留现有 CLI 兼容 helper，但改为复用 trade 层实现。

## 3. Verification

- [x] 3.1 补充 `TradeManager` 和 trade context 测试。
- [x] 3.2 补充 CLI 分发测试，验证平安交易命令调用 `TdxTradeManager`。
- [x] 3.3 运行定向测试验证新增 trade manager 不影响既有 manager/task/CLI 入口。
