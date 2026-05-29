## Why

Subscription-watch now has restart backoff, explicit single-step supervisor tick, and local statefile ownership diagnostics. The next lifecycle gap is an operator-visible bounded foreground supervisor run that can repeatedly evaluate tick state without introducing a daemon, scheduler, or automatic background retry loop.

## What Changes

- Add a bounded `supervisor_run()` operation that calls existing `supervisor_tick()` at most `max_ticks` times.
- Stop early when a tick recovers, no-ops, or fails; keep waiting ticks bounded by `max_ticks`.
- Expose the operation through worker bridge HTTP, registry helper, and CLI.
- Preserve the boundary: foreground operator call only; no background daemon, no scheduler/timer ownership, no provider readiness guarantee, and no workflow execution.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: background control supports an explicit bounded foreground supervisor run over the existing tick operation.
- `tdx-worker-bridge-http-control-plane`: worker bridge exposes a bounded supervisor-run control route and CLI/registry dispatch.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Tests: focused background controller, bridge HTTP, bridge registry, and CLI dispatch tests.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]`.

