## Why

D-07/D-08 still list process/window lifecycle ownership as a remaining desktop lifecycle gate. Current PingAn `dialog_readiness` records the configured `title_keyword` and `exe_path`, but it does not expose a passive runtime/window observation in the lifecycle payload.

## What Changes

- Add read-only observed process/window ownership status to PingAn `dialog_readiness`.
- Reuse existing PingAn runtime/window health discovery to record whether the runtime and top-level trading window were observed.
- Keep the status non-side-effecting: no process start/stop, no lock/statefile ownership, no restart/backoff, no order submission, and no dialog control dispatch.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose passive process/window ownership observation in lifecycle readiness.
- `tdx-desktop-trading-safety`: register passive process/window observation as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the observation without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
