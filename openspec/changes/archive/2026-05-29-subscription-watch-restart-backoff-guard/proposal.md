## Why

Explicit subscription-watch restart can now stop an active run and attempt a replacement, but a replacement start failure leaves operators with only an immediate error. A minimal bounded backoff guard prevents repeated manual restart attempts from hammering the provider path while preserving the current no-supervisor boundary.

## What Changes

- Record a compact `restart_backoff` state when explicit restart stops the active run but replacement `start()` fails.
- Reject subsequent explicit `restart()` attempts while the recorded backoff window is still active, returning stable retry metadata.
- Include `BACKOFF_ACTIVE` in restart preflight and project the compact backoff summary into diagnostics.
- Keep this as an explicit operator guard only: no automatic restart, no retry loop, no long-running supervisor, no readiness or ownership proof.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: explicit restart records and enforces bounded backoff after replacement start failure.
- `tdx-subscription-long-run-status-summary`: diagnostics exposes compact restart backoff state when present.
- `tdx-worker-bridge-http-control-plane`: worker bridge diagnostics preserves the backoff summary without executing lifecycle control.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_status_diagnostics.py`.
- Tests: focused background controller, bridge HTTP diagnostics, and CLI diagnostics coverage.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]` with explicit evidence and non-goals.
