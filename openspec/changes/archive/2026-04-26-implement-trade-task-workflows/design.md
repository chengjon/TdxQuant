## Context

现有 `TdxTaskManager` 只依赖 `TdxApiManager`，因此：

- 可以做板块研究
- 可以做公式扫描
- 可以做导出

但无法调度 `TdxTradeManager`，这让 task 层与桌面交易 capability 之间仍有断层。

## Goals

- 让 `TdxTaskManager` 可以同时持有 API manager 与 Trade manager。
- 新增最小可用交易 workflow task。
- 维持 task 层“场景编排，不重写底层实现”的原则。

## Non-Goals

- 本次不做复杂的买入前行情规则引擎。
- 本次不实现卖出、撤单或回报读取 workflow。
- 本次不重构现有 `trade` CLI 或 `TdxTradeManager` 结构。

## Decisions

### 1. Task 层正式同时编排 API 与 Trade

`TdxTaskManager` 新增：

- `trade_manager`

初始化时允许传入：

- `trade_profile`
- `trade_profile_overrides`
- `title_keyword`
- `exe_path`

这样 task 层仍然是唯一顶层 workflow 入口，而底层 capability 归属保持独立。

### 2. 先提供两个最小交易 workflow

新增：

- `trade_buy(...)`
- `trade_submit_once(...)`

两者都支持：

- 可选先 `refresh_environment(...)`
- 再执行对应 `trade_manager.pingan.*`

### 3. CLI 挂到 `task` 命名空间

新增：

- `task trade-buy`
- `task trade-submit-once`

参数基本复用现有稳定交易命令，以降低学习成本。

### 4. Profile 控制是否预刷新

在 `runtime/task-profiles.json` 中为交易 workflow 增加：

- `trade_profile`
- `refresh_before_trade`
- `refresh_market`
- `refresh_force`

CLI 可通过显式参数覆盖。

## Verification

- `TdxTaskManager` 单元测试验证 refresh + trade 组合编排。
- CLI 测试验证新 task 子命令分发。
- 回归测试验证已有 task/API/trade 入口不受影响。
