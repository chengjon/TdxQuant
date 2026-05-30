## Why

D-07/D-08 still list exception popup handling as a remaining desktop lifecycle gate. The current `dialog_readiness` workflow can locate confirm/result dialogs but does not expose a separate, read-only signal for whether a visible result dialog appears to be an exception/error popup.

## What Changes

- Add passive exception popup lookup evidence to PingAn `dialog_readiness`.
- Include `exception_popup_lookup` in `desktop_lifecycle_gate_status.dialog_checks` when result dialog readiness is requested.
- Keep the workflow non-side-effecting: no order submission, no dialog close, no click, no retry, no recovery.
- Register the evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-dialog-readiness`: expose passive exception popup lookup status in dialog readiness.
- `tdx-desktop-trading-safety`: register passive exception popup lookup as partial lifecycle evidence only.
- `tdx-function-tree-registry`: require D-07/D-08 to record the lookup evidence without claiming implemented status.

## Impact

- `tdxquant/trade/manager.py`
- `tests/test_trade_manager.py`
- `FUNCTION_TREE.md`
- OpenSpec specs for dialog readiness, desktop trading safety, and FUNCTION_TREE registry

