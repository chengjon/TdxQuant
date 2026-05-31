## Why

PingAn preflight can now report local lifecycle owner lock status, but callers cannot yet ask preflight to fail when that local owner lock is missing, stale, or held by another token. A read-only requirement gate makes the status actionable before any operator chooses a side-effecting trade command.

## What Changes

- Add an optional `require_lifecycle_owner_lock` flag to `TdxTradeManager.pingan.preflight(...)`.
- Add matching `trade preflight --require-lifecycle-owner-lock` CLI support.
- Extend `promotion_gate_status.lifecycle_owner_lock_status` with requirement fields such as `required`, `owner_token_matches`, and `requirement_status`.
- Keep the gate read-only: no owner lock acquire/release, no order submission, and no process lifecycle control.
- Keep D-07/D-08 as `[部分实现]`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-desktop-trading-preflight`: preflight can fail read-only when a required local owner lock is not owned by the caller token.
- `tdx-desktop-trading-cli-entry`: `trade preflight` accepts `--require-lifecycle-owner-lock`.
- `tdx-desktop-trading-safety`: required owner-lock preflight gate remains a local statefile safety check, not live readiness.
- `tdx-function-tree-registry`: D-07/D-08 register the required owner-lock preflight gate as partial evidence only.

## Impact

- Code: `tdxquant/trade/manager.py`, `tdxquant/cli.py`.
- Tests: focused manager, CLI, and FUNCTION_TREE registry coverage.
- No default behavior change when the flag is omitted.
