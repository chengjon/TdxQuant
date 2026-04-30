## Why

桌面交易线已经有稳定 `trade health` 和 `trade preflight`，但当前剩余交易治理缺口仍然集中在 confirm/result dialog 边界。现有 dialog lookup 逻辑散落在低层执行函数里，调用者缺少一个稳定、无副作用的入口来回答“当前弹窗如果已经出现，稳定路径是否能识别它”。

## What Changes

- Add a stable non-side-effecting `dialog_readiness` workflow at `TdxTradeManager.pingan.dialog_readiness(...)`.
- Add nested CLI entry `trade dialog-readiness`.
- Evaluate current confirm/result dialog lookup readiness using the stable dialog lookup rules and configured lookup mode.
- Support explicit `require_visible` semantics so callers can choose between passive observation and hard readiness enforcement.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-dialog-readiness`: Stable desktop trade management exposes a read-only confirm/result dialog readiness workflow.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: The nested `trade` CLI gains a stable `dialog-readiness` subcommand.

## Impact

- Affected code:
  - `tdxquant/trade/manager.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
