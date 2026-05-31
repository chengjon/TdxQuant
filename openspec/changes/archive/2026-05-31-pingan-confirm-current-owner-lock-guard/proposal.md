## Why

D-07 now has an opt-in lifecycle owner-lock execution guard for PingAn buy/sell/submit_once and guarded buy paths, but `confirm_current` remains an uncovered side-effecting confirmation path. This change closes that bounded guard-forwarding gap without claiming broker readiness or full trading workflow completion.

## What Changes

- Add optional lifecycle owner-lock guard parameters to `TdxTradeManager.pingan.confirm_current(...)`.
- Expose the same guard options on stable `trade confirm-current` and `task trade-confirm-current` CLI/task entrypoints.
- Keep default behavior unchanged when the guard is not requested.
- Register the new evidence in `FUNCTION_TREE.md` while keeping D-07 `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-safety`: PingAn confirm-current shall honor the opt-in lifecycle owner-lock execution guard before advancing a confirmation dialog.
- `tdx-api-cli-entry`: Stable confirm-current CLI entrypoints shall accept and forward lifecycle owner-lock guard options.
- `tdx-task-management`: Task confirm-current shall accept and forward lifecycle owner-lock guard options to the PingAn manager method.
- `tdx-function-tree-registry`: D-07 shall cite confirm-current owner-lock guard evidence while preserving partial status and explicit boundaries.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: focused PingAn trade manager, task manager, CLI parser/dispatch, and FUNCTION_TREE registry tests.
- Runtime behavior remains opt-in; no lifecycle owner acquisition/release, supervisor behavior, broker readiness, live trading acceptance, or workflow execution is introduced.
