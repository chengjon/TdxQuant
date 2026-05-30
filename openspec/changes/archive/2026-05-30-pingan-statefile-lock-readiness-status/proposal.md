## Why

D-07/D-08 still list process/window lifecycle ownership as a remaining desktop lifecycle gate. Current PingAn `dialog_readiness` exposes runtime/window observation, but it does not make statefile or lock ownership status explicit.

## What Changes

- Add a read-only `statefile_lock_status` payload to PingAn `desktop_lifecycle_gate_status`.
- Report artifact target paths and explicitly state that no statefile lock, owner token, state write, ledger write, or audit write was acquired or executed.
- Preserve current behavior: no lock acquisition, no statefile write, no process ownership, no supervisor control, no order submission.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose read-only statefile/lock status in lifecycle readiness.
- `tdx-desktop-trading-safety`: register statefile/lock status as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the status without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
