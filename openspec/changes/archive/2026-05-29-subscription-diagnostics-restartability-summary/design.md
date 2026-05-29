# Design

## Behavior

The diagnostics view SHALL add:

```json
"restartability": {
  "ready": true,
  "decision": "ready",
  "reason_codes": [],
  "has_start_request": true,
  "start_request_summary": {
    "stock_count": 2,
    "has_max_events": true,
    "has_max_seconds": true,
    "has_poll_interval": true
  },
  "boundary": "read_only;does_not_stop_start_or_schedule_restart"
}
```

The projection is derived from the already fetched detailed watch-status payload:

- `control.state` / `control.active` determine active-run presence.
- `control.start_request` determines whether restart metadata exists and is shape-valid enough for a preflight hint.
- `status_summary` and existing diagnostics rollups continue to supply all other diagnostics fields.

## Reason Codes

- `NO_ACTIVE_RUN`: no active control state is visible.
- `MISSING_START_REQUEST`: active state exists but does not include a dict `start_request`.
- `INVALID_START_REQUEST`: `start_request` exists but lacks non-empty string `stock_list` or has invalid optional numeric fields.

## Boundaries

The diagnostics projection remains read-only. It MUST NOT:

- Call `restart_preflight()`, `restart()`, `stop()`, or `start()`.
- Read PID files or acquire locks beyond the existing watch-status call.
- Signal processes.
- Schedule restart/backoff or run a supervisor loop.
- Claim health/readiness, process ownership, or production governance completeness.

## Compatibility

The new `restartability` object is additive under `result.diagnostics`. Existing diagnostics fields remain unchanged.
