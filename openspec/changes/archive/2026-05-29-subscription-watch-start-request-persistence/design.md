# Design: Subscription Watch Start Request Persistence

## Scope

This change persists the operator's normalized start request in the worker-local active state written by `SubscriptionWatchBackgroundController.start()`.

The persisted request is an ownership and restart/backoff prerequisite, not a restart/backoff implementation.

## State Shape

`active.json` SHALL include:

```json
{
  "start_request": {
    "stock_list": ["600519.SH"],
    "max_events": 10,
    "max_seconds": 30.0,
    "poll_interval": 0.5
  }
}
```

Rules:

- `stock_list` is copied as the exact normalized list accepted by the start validator.
- Optional numeric fields are present with their requested value or `null`.
- Same-idempotency replay returns the current active payload including `start_request`.
- Status responses expose this metadata as part of raw `control`, because raw `control` already represents active worker-local ownership state.

## Non-goals

- No new `restart` command or HTTP endpoint.
- No reconnect/backoff scheduler, retry timer, supervisor loop, or auto-recovery.
- No PID liveness model changes, lock protocol changes, or process ownership inference.
- No new summary/diagnostics projection fields.
- No mutation of completed historical run artifacts.

