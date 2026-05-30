## Why

D-07/D-08 still list process/window lifecycle ownership as a remaining desktop lifecycle gate. Current PingAn `dialog_readiness` records observed process/window and statefile/lock non-ownership, but it does not expose a stable status for lifecycle control actions such as start, stop, restart, supervisor ownership, or backoff.

## What Changes

- Add a read-only `lifecycle_control_status` payload to PingAn `desktop_lifecycle_gate_status`.
- Report that dialog readiness does not start, stop, restart, supervise, kill, or back off the PingAn desktop process.
- Preserve current behavior: no process mutation, no supervisor ownership, no restart/backoff, no state/ledger/audit writes, and no order submission.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose read-only lifecycle control status in lifecycle readiness.
- `tdx-desktop-trading-safety`: register lifecycle control status as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the status without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
