# Design

## Behavior

`SubscriptionWatchBackgroundController.restart_preflight()` SHALL reconcile current background state and return a stable read-only envelope:

- `schema_version`: `tdx.subscription_watch.restart_preflight.v1`
- `ready`: boolean
- `decision`: `ready` or `blocked`
- `reason_codes`: stable string list
- `run_id`, `state`, and active/start-request presence flags
- `start_request_summary`: compact metadata such as `stock_count`, `has_max_events`, `has_max_seconds`, and `has_poll_interval`
- `boundary`: explicit read-only marker

The method SHALL NOT call `stop()`, `start()`, signal processes, write state files, or schedule restart/backoff.

## Readiness Rules

The preflight is `ready=true` only when:

- Reconciled state is in an active process state.
- A persisted `start_request` is present.
- The persisted `start_request` is valid enough to replay through `start()`: non-empty string `stock_list`, optional numeric `max_events`, `max_seconds`, and `poll_interval`.

Blocked cases use stable reason codes:

- `NO_ACTIVE_RUN`
- `MISSING_START_REQUEST`
- `INVALID_START_REQUEST`

The view is intentionally a restartability preflight, not a health or production readiness proof.

## Interfaces

- HTTP: `GET /bridge/v1/watch/restart-preflight`
- Registry helper: `run_bridge_watch_restart_preflight(...)`
- CLI: `bridge watch-restart-preflight --registry ... --worker ...`

All surfaces preserve the controller result and must remain read-only.

## Non-Goals

- No automatic restart.
- No retry timer, backoff scheduler, or supervisor loop.
- No restart policy.
- No readiness gate or health proof beyond restartability inputs.
- No PID ownership model changes.
- No event-stream/SSE behavior changes.
