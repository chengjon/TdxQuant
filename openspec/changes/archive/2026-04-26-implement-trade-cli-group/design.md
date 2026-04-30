## Context

当前 CLI 已有两种成熟模式：

- `api` 二级命令
- `task` 二级命令

桌面交易侧虽然已有 `TdxTradeManager`，但命令层仍停留在扁平阶段。既然 capability 已独立，CLI 也应开始按相同方法治理。

## Goals

- 新增 `trade` 二级命令组。
- 先只暴露稳定平安买入命令。
- 与扁平命令共存，不做破坏性迁移。

## Non-Goals

- 本次不迁移实验性 Win32/UIA/HID 诊断命令。
- 本次不引入多券商命名空间。
- 本次不移除旧扁平命令。

## Decisions

### 1. `trade` 组只先承载稳定命令

先提供：

- `trade buy`
- `trade submit-once`

这两个命令都复用 `TdxTradeManager.pingan.*`，只是在 CLI 层提供新的标准入口。

### 2. 参数与扁平命令保持等价

为了降低迁移成本：

- `trade buy` 与 `pingan-buy` 参数保持等价
- `trade submit-once` 与 `pingan-buy-submit-once` 参数保持等价

这样用户可以逐步切换，不必重新记忆稳定命令的参数体系。

### 3. 分发逻辑单独收敛到 `_handle_trade_subcommand`

和 `api` / `task` 一样，新增独立的 trade 分发函数，避免继续把 `main()` 的条件分支无限膨胀。

### 4. 扁平命令作为兼容入口保留

现有扁平命令继续存在，但它们和新 `trade` 命令共用同一套 manager 执行路径。

## Verification

- parser 测试覆盖 `trade buy` / `trade submit-once`
- 分发测试验证 `trade` 子命令走 `TdxTradeManager`
- 回归测试验证旧扁平交易命令仍可用
