## Why

The PingAn lifecycle owner lock now records a local owner token and owner PID, but status output does not yet validate whether that recorded PID is still alive. Adding local PID validation makes stale ownership diagnostics more useful before any real process lifecycle control is introduced.

## What Changes

- Add owner PID validation fields to PingAn lifecycle owner lock status/acquire/release payloads.
- Report the recorded owner PID, whether PID validation ran, and a normalized PID status such as `alive`, `not_alive`, or `missing`.
- Keep the validation local and non-controlling: no process kill, no restart, no supervisor ownership, no desktop PID claim, no order submission, and no trade artifact writes.
- Register the new evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-management`: extends PingAn lifecycle owner lock status with local owner PID validation.
- `tdx-desktop-trading-safety`: records that PID validation does not claim or control the PingAn desktop process.
- `tdx-function-tree-registry`: requires D-07/D-08 to cite owner PID validation without status promotion.

## Impact

- Affected code: `tdxquant/trade/manager.py`
- Affected tests: `tests/test_trade_manager.py`, `tests/test_function_tree_registry.py`
- Affected registry: `FUNCTION_TREE.md`
