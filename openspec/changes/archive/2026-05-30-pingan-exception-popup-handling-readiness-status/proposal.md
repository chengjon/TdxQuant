## Why

D-07/D-08 still list exception popup handling as a remaining desktop lifecycle gate. Current PingAn `dialog_readiness` can detect exception-like result popup text, but it does not expose a stable status that says handling is unavailable and manual intervention is required.

## What Changes

- Add a read-only `exception_popup_handling_status` payload to PingAn `desktop_lifecycle_gate_status`.
- Derive the status from the existing passive `exception_popup_lookup` check.
- Report that handling is not available in this workflow: no popup close, no confirm click, no recovery, no retry, and no resubmission.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose read-only exception popup handling status in lifecycle readiness.
- `tdx-desktop-trading-safety`: register exception popup handling status as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the status without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry
