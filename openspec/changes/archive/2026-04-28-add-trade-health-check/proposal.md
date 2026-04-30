## Why

桌面交易线已经有稳定买入入口、`trade_safety` 摘要和 submission ledger，但还缺一个正式、无副作用的健康检查入口。当前虽然有 `pingan-probe`、`tdx-trade-probe`、`hid-ping` 等低层诊断命令，上层调用者仍然缺少一个能直接回答“当前稳定交易路径是否可用”的标准化管理面。

## What Changes

- Add a stable non-side-effecting desktop trade health workflow at `TdxTradeManager.pingan.health(...)`.
- Add nested CLI entry `trade health`.
- Return normalized health summary covering broker/runtime window readiness, current trade profile context, trade artifact target paths, and optional HID ping status when a port is provided.
- Keep the health workflow read-only: it must not write last-order state, event log, or submission ledger artifacts.

## Capabilities

### New Capabilities
- `tdx-desktop-trading-health`: Stable desktop trade management exposes a read-only broker/runtime preflight workflow.

### Modified Capabilities
- `tdx-desktop-trading-cli-entry`: The nested `trade` CLI gains a stable `health` subcommand.

## Impact

- Affected code:
  - `tdxquant/trade/manager.py`
  - `tdxquant/trade/context.py`
  - `tdxquant/cli.py`
  - `tests/test_trade_manager.py`
  - `tests/test_api_cli.py`
- Affected docs:
  - `docs/TdxQuant_Project_Function_Map.md`
  - `docs/TdxQuant_Next_Steps.md`
