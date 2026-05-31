## Why

D-07 now has opt-in lifecycle owner-lock guards on buy/sell/submit_once/confirm_current and guarded buy paths, but `submit_ready` remains uncovered even though it can drive the desktop into the manual confirmation boundary. This change closes that bounded pre-execution guard gap without claiming broker readiness or full trading workflow completion.

## What Changes

- Add optional lifecycle owner-lock guard parameters to `TdxTradeManager.pingan.submit_ready(...)`.
- Expose and forward the same guard options on stable `trade submit-ready` and `task trade-submit-ready` entrypoints.
- Preserve default submit-ready behavior when guard options are omitted.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07 `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-safety`: PingAn submit-ready shall honor the opt-in lifecycle owner-lock execution guard before running the HID submit probe.
- `tdx-api-cli-entry`: Stable submit-ready CLI entrypoints shall accept and forward lifecycle owner-lock guard options.
- `tdx-task-management`: Task submit-ready shall accept and forward lifecycle owner-lock guard options to the PingAn manager method.
- `tdx-function-tree-registry`: D-07 shall cite submit-ready owner-lock guard evidence while preserving partial status and explicit boundaries.

## Impact

- Affected code: `tdxquant/trade/manager.py`, `tdxquant/api/task.py`, `tdxquant/cli.py`.
- Affected tests: focused PingAn trade manager, task manager, CLI parser/dispatch, and FUNCTION_TREE registry tests.
- Runtime behavior remains opt-in; no lifecycle owner acquisition/release, supervisor behavior, broker readiness, live trading acceptance, or workflow execution is introduced.
