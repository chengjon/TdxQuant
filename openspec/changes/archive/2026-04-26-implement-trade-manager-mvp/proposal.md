## Why

桌面自动化交易 capability 已经完成独立规划，但当前生产可用路径仍然主要表现为：

- `pingan-buy` / `pingan-buy-submit-once` 等扁平 CLI 命令
- `tdxquant/desktop/uia.py` 中的实操流程函数
- `cli.py` 中分散的 profile、状态回填、合同号输出逻辑

这导致桌面交易虽然已经具备真实可用闭环，却还没有正式的顶层管理面。继续把稳定逻辑散放在 CLI 中，会让后续的 task 编排、统一 profile、耗时统计、状态文件/日志回填和多券商扩展都缺少挂载点。

现在需要实现一个最小可用的 `TradeManager`，先把平安证券稳定买入路径收进独立 capability 的管理层。

## What Changes

- 新增 `tdxquant/trade/` 包，提供 `TdxTradeManager` 作为桌面交易顶层管理入口。
- 为桌面交易增加独立 profile 文件 `runtime/trade-profiles.json`。
- 将平安买入稳定路径的 profile 解析、manager metadata、耗时包装、状态文件回填和事件日志回填收敛到 `TradeManager`。
- 保持现有 `pingan-buy` / `pingan-buy-submit-once` CLI 命令兼容，但改为通过 `TdxTradeManager` 执行。
- 补充 `TradeManager` 与 CLI 分发测试。

## Capabilities

### Modified Capabilities

- `tdx-desktop-trading-management`

## Impact

- 形成桌面交易 capability 的第一个正式顶层管理入口。
- 保持现有平安交易 CLI 和底层 Win32/UIA/HID 闭环不变，降低实机回归风险。
- 为后续 `trade` 二级命令、交易 task 层和更多券商适配预留稳定的上层入口。
