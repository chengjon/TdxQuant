## 1. Task Manager Expansion

- [x] 1.1 为 `TdxTaskManager` 引入 `TdxTradeManager` 依赖与初始化参数。
- [x] 1.2 新增 `trade_buy` workflow task，支持可选环境刷新后执行买入。
- [x] 1.3 新增 `trade_submit_once` workflow task，支持可选环境刷新后执行完整提交流程。

## 2. CLI And Profiles

- [x] 2.1 为 `task` 二级命令新增 `trade-buy`。
- [x] 2.2 为 `task` 二级命令新增 `trade-submit-once`。
- [x] 2.3 为交易 workflow task 增加默认 profile。
- [x] 2.4 更新 task 使用文档。

## 3. Verification

- [x] 3.1 补充 task manager 交易 workflow 测试。
- [x] 3.2 补充 CLI 分发测试。
- [x] 3.3 运行定向测试验证新增 task workflow 不影响既有 API/task/trade 入口。
