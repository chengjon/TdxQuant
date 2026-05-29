## Why

Subscription-watch now records explicit restart backoff after a failed replacement start, but there is no bounded way to consume that state once the backoff expires. A single operator-triggered supervisor tick is the smallest lifecycle step toward recovery without introducing a long-running supervisor loop.

## What Changes

- Add a `supervisor_tick()` control operation that evaluates current restart backoff state once.
- When backoff is still active, return a no-op wait result without calling `start()`.
- When backoff has expired and a valid persisted `start_request` exists, attempt one replacement `start()` and return a compact recovery result.
- Add worker bridge HTTP/registry/CLI entry points for the explicit tick.
- Preserve the boundary: no background loop, no automatic scheduling, no health/readiness proof, and no provider ownership inference.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: background control supports a bounded explicit supervisor tick over restart backoff state.
- `tdx-worker-bridge-http-control-plane`: worker bridge exposes an explicit supervisor-tick control endpoint without changing status/events/restart behavior.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Tests: focused background controller, bridge HTTP, bridge registry, and CLI dispatch tests.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]`.
