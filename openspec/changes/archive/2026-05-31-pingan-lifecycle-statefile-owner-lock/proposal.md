## Why

D-07/D-08 now expose several read-only PingAn lifecycle readiness fields, but the registry still lacks a concrete, opt-in ownership primitive that can write a local lifecycle statefile and prove who owns lifecycle work. Adding a small local owner lock is the next promotion-gate step before any real process start/stop/restart/supervisor work.

## What Changes

- Add an explicit PingAn lifecycle owner lock manager surface for `status`, `acquire`, and `release`.
- Persist a local lifecycle ownership statefile and sibling lock file only when the caller explicitly requests `acquire` or `release`.
- Report lock status, owner token, stale detection, lock/statefile paths, and non-execution boundaries in a stable result payload.
- Keep desktop process lifecycle control out of scope: no start, stop, restart, kill, supervisor loop, backoff execution, broker readiness, order submission, or trade artifact writes.
- Register the new evidence in `FUNCTION_TREE.md` while keeping D-07/D-08 `[部分实现]`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-desktop-trading-management`: adds the explicit PingAn lifecycle owner lock manager surface.
- `tdx-desktop-trading-safety`: records that owner-lock evidence is statefile-only and cannot satisfy live trading implementation gates by itself.
- `tdx-function-tree-registry`: requires D-07/D-08 to cite owner-lock evidence without status promotion.

## Impact

- Affected code: `tdxquant/trade/manager.py`
- Affected tests: `tests/test_trade_manager.py`, `tests/test_function_tree_registry.py`
- Affected registry: `FUNCTION_TREE.md`
