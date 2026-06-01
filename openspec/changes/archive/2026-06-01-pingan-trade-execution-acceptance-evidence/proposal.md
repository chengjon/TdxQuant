## Why

D-07 and D-08 now have implemented trading entrypoints, safety gates, lifecycle controls, and task-side acceptance evidence. The remaining usability gap is that the `trade` namespace does not expose a direct read-only acceptance evidence summary for operators to inspect before any manual/live review.

## What Changes

- Add a read-only PingAn trade execution acceptance evidence summary on the `TdxTradeManager.pingan` boundary.
- Add a `trade acceptance-evidence` CLI command that returns the summary without executing trade commands or desktop automation.
- Register the new evidence boundary in `FUNCTION_TREE.md` without changing D-07/D-08 status or claiming production readiness.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-management`: exposes a read-only PingAn acceptance evidence summary over the implemented trade execution surface.
- `tdx-desktop-trading-cli-entry`: adds a stable `trade acceptance-evidence` read-only command.
- `tdx-function-tree-registry`: registers the new acceptance evidence summary in the single feature registry.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_trade_manager.py`, `tests/test_api_cli.py`.
- Affected docs/registry: `FUNCTION_TREE.md`, OpenSpec specs.
- No real order placement, desktop process control, UIA/HID automation, broker readiness probe, task workflow execution, or status transition is introduced.
