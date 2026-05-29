## Why

Subscription-watch now has restart backoff and an explicit supervisor tick, but B-16/E-09 still lacks a stable read-only ownership view over the local lifecycle files that those controls depend on. Operators can see status and backoff posture, but they cannot verify whether the active statefile, pidfile, and lockfile describe the same local process boundary.

## What Changes

- Add a compact `statefile_ownership` diagnostic to subscription-watch background status.
- Derive the diagnostic from existing `active.json`, `pid`, and `lock` files plus local PID liveness checks.
- Project the same diagnostic through bridge `watch/status?view=diagnostics`.
- Preserve the boundary: this is local statefile/pidfile evidence only; it does not acquire the control lock, start/stop/restart a worker, create a supervisor loop, or prove provider readiness.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: background status includes read-only statefile ownership diagnostics.
- `tdx-worker-bridge-http-control-plane`: diagnostics view exposes the compact ownership diagnostic without returning raw control/watch payloads.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/subscription_watch_status_diagnostics.py`.
- Tests: focused background controller and bridge diagnostics tests.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]`.

