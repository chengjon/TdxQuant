## Why

D-07 lists Ping An buy, sell, and confirm-current together, but stable daily entrypoints currently make buy and confirm-current easier to discover than sell. The existing `TdxTradeManager.pingan.sell` path should be exposed through the same stable CLI/task layer with explicit safety controls and evidence.

## What Changes

- Add a stable nested `trade sell` CLI command that dispatches through the existing trade service path with `OrderSide.SELL`.
- Add a task-level `trade-sell` workflow that calls `TdxTradeManager.pingan.sell` with the same refresh and safety-control pattern as `trade-buy`.
- Update `FUNCTION_TREE.md` D-07 evidence and boundary without claiming broader broker or exception coverage.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`: add stable sell entrypoint alongside buy and submit-once.
- `tdx-task-management`: add stable sell workflow task alongside existing trade buy task.

## Impact

- Affected code: `tdxquant/cli.py`, `tdxquant/api/task.py`, `tdxquant/tasking.py`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_api_manager.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
