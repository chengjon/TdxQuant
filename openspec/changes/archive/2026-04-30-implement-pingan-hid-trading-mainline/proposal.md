## Why

当前真实交易方向已经明确收口到 `PingAN + HID`，而 `TongDaXin` 交易线按范围关闭。现有代码虽然已经有 `PingAn` 买入/卖出快路径和买入 `submit_once` 链路，但还没有把 `PingAN + HID` 收口成对称、稳定的 live-trading 主线，卖出完整提交流程、task/preset 入口和主线口径仍然缺失。

## What Changes

- 将 `PingAN + HID` 明确为当前项目唯一的真实交易执行主线，`TongDaXin` 交易仅保留桥接/探测基线，不再作为 live-trading 依赖。
- 补齐 `PingAn` 卖出完整提交流程，使 `buy/sell` 在快路径和 `submit_once` 路径上都具备对称的稳定能力。
- 让现有 `TradeService + PingAnDesktopTraderGateway` 正式承接 `PingAN` live-trading 主线，而不是继续把卖出和完整提交流程留在零散兼容路径里。
- 在 `trade` CLI 和 task 层补齐卖出稳定入口、preset/default profile 和兼容转发，保证日常调用不再只覆盖买入。
- 保持现有审计、提交台账和 split-step 边界命令不破坏；本批次不恢复 `TongDaXin` 真实交易，也不扩到撤单、账户、持仓。

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `tdx-desktop-trading-management`: 将 `PingAN + HID` 固化为真实交易主线，并要求稳定买卖流程在快路径和 `submit_once` 路径上都可用。
- `tdx-desktop-trading-cli-entry`: 增加稳定卖出/卖出完整提交 CLI 入口与对应 preset 能力，同时保留现有买入兼容命令。
- `tdx-task-management`: 增加稳定卖出 task 工作流与 preset 入口，并要求其通过当前交易主线透传安全控制与标准化产物。

## Impact

- 受影响代码主要在 `tdxquant/desktop/uia.py`、`tdxquant/trade/manager.py`、`tdxquant/trader/adapters/pingan_desktop.py`、`tdxquant/cli.py`、`tdxquant/api/task.py`、`tdxquant/tasking.py`。
- 运行时配置会扩展 `runtime/trade-presets.json` 与 `runtime/task-presets.json` 的卖出默认项；现有 `PingAn` 审计和台账文件继续沿用。
- 不引入新外部依赖；主要变化是把现有 `PingAn` HID 链路补齐并收口成正式主线。
