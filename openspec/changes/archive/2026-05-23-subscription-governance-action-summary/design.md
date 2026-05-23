## Context

`build_subscription_watch_status_summary()` already computes:

- `overall_status` from control/watch status state.
- heartbeat and watermark staleness only when explicit thresholds are supplied.
- advisory `governance.decision` and `governance.reasons`.

The missing piece is a machine-readable hint that tells a caller which manual review category is implied by those reasons.

## Design

Add a deterministic `actions` array to the governance object:

- `observe` decisions return an empty list.
- Resilience states (`overall_status:reconnecting`, `overall_status:degraded`, `overall_status:failed`) return a review action that names the relevant status and recommends checking long-run process health.
- Stale heartbeat and stale watermark reasons return separate review actions so callers can distinguish transport liveness from event-flow freshness.

Each action is advisory data with a stable shape:

- `action`: a short machine-readable action id.
- `reason`: the existing reason string that triggered the action.
- `severity`: `review`.
- `description`: short human-readable context.

The implementation will derive actions from the existing reasons list inside `_build_subscription_watch_governance_summary()`. It will not call any controller method, mutate state, schedule reconnect/backoff, or affect bridge event-stream behavior.

## Boundaries

- This does not add automated reconnect/backoff/restart.
- This does not change `SubscriptionWatchBackgroundController.start/stop/list/events/logs`.
- This does not infer staleness unless explicit stale thresholds were passed.
- Existing fields remain additive-compatible.
