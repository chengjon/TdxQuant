## Why

桌面交易 capability 已经具备：

- 独立规格
- `TdxTradeManager`
- 现有平安稳定买入 CLI 兼容入口

但命令层仍以扁平形式存在，日常调用仍然依赖：

- `pingan-buy`
- `pingan-buy-submit-once`

这与已经建立的 `api` / `task` 二级命令结构不一致，也不利于后续继续扩展稳定交易入口。

现在需要引入 `trade` 二级命令组，先把稳定平安买入命令挂载到新的标准命名空间下，同时保留现有扁平命令兼容。

## What Changes

- 在 CLI 中新增 `trade` 二级命令组。
- 新增稳定交易子命令：
  - `trade buy`
  - `trade submit-once`
- 复用现有 `TdxTradeManager` 执行逻辑，不重写底层交易实现。
- 保留 `pingan-buy` / `pingan-buy-submit-once` 扁平命令兼容。
- 补充 parser、分发与文档测试。

## Capabilities

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`

## Impact

- 项目形成正式的桌面交易嵌套 CLI 命名空间。
- 稳定交易命令有了与 `api` / `task` 并列的统一入口。
- 为后续继续把更多稳定交易动作纳入 `trade` 组提供落点。
