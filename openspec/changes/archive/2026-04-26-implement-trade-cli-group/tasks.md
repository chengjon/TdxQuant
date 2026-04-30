## 1. Trade CLI

- [x] 1.1 新增 `trade` 二级命令组。
- [x] 1.2 新增 `trade buy`，并复用 `TdxTradeManager`。
- [x] 1.3 新增 `trade submit-once`，并复用 `TdxTradeManager`。
- [x] 1.4 保持现有扁平交易命令兼容，并尽量复用相同执行路径。

## 2. Verification

- [x] 2.1 补充 parser 与分发测试。
- [x] 2.2 运行定向测试验证 `trade` 新入口和旧扁平入口都可用。
