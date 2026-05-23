## Why

The subscription long-run status summary currently exposes heartbeat timestamps but always reports heartbeat staleness as `not_evaluated`. Operators need a deterministic, opt-in way to ask whether a persisted heartbeat is stale while keeping default status views and reconnect scheduling unchanged.

## What Changes

- Add opt-in heartbeat staleness evaluation to `build_subscription_watch_status_summary(...)`.
- Allow `SubscriptionWatchBackgroundController.status(...)` to accept a heartbeat stale threshold and evaluation time.
- Allow the bridge HTTP `watch/status` endpoint and bridge CLI proxy to forward an optional `heartbeat_stale_after_seconds` threshold.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary to show this is status evaluation only, not reconnect/backoff automation.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `tdx-subscription-long-run-status-summary`: Add opt-in wall-clock heartbeat staleness evaluation while preserving default non-evaluating behavior.

## Impact

- Affected code: subscription background status summary, bridge HTTP watch-status query handling, bridge registry route building, bridge CLI parser/handler, focused tests, and `FUNCTION_TREE.md`.
- No external dependencies.
- No change to process lifecycle, reconnect scheduling, SSE stream semantics, or artifact schemas beyond additive summary fields.
