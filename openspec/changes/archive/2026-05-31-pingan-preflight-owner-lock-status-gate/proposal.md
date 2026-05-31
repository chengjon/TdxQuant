## Why

D-07/D-08 now have a local PingAn lifecycle owner lock and explicit operator CLI, but the stable read-only `trade preflight` path does not surface that ownership state beside provider and safety gate evidence. Operators need one preflight result that can show whether a caller-supplied owner statefile/token is present, stale, and PID-diagnosed without acquiring locks or dispatching a trade.

## What Changes

- Add optional PingAn lifecycle owner lock status inputs to `TdxTradeManager.pingan.preflight(...)`.
- Add matching optional `trade preflight` CLI arguments for statefile path, owner token, and stale timeout.
- Add a non-side-effecting `promotion_gate_status.lifecycle_owner_lock_status` summary.
- Keep D-07/D-08 as `[部分实现]` and record the new evidence/boundary in `FUNCTION_TREE.md`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-desktop-trading-preflight`: preflight may include a read-only PingAn lifecycle owner lock status gate.
- `tdx-desktop-trading-cli-entry`: `trade preflight` accepts optional lifecycle owner lock status arguments.
- `tdx-desktop-trading-safety`: PingAn owner lock status inside preflight remains a local read-only gate and does not imply live readiness.
- `tdx-function-tree-registry`: D-07/D-08 register the preflight owner lock status gate as partial evidence only.

## Impact

- Code: `tdxquant/trade/manager.py`, `tdxquant/cli.py`.
- Tests: focused manager, CLI parser/dispatch, and FUNCTION_TREE registry tests.
- Docs/specs: OpenSpec deltas plus `FUNCTION_TREE.md` evidence and boundary updates.
- No external dependencies, no order execution, and no process lifecycle control.
