# provider replay lifecycle backoff summary design

## Context

Provider replay currently has no supervisor loop and no automatic restart/backoff behavior. The lifecycle operation summary marks `backoff` as blocked. A dedicated backoff summary makes the current boundary explicit while preserving a stable shape for future implementation.

## Design

Add `lifecycle.backoff_summary` with this current shape:

- `backoff_status`: `not_configured`
- `enabled`: `false`
- `policy`: `not_managed`
- `retry_count`: `0`
- `delay_window_seconds`: `null`
- `last_failure_reason`: `null`
- `next_retry_status`: `not_scheduled`
- `next_retry_pending`: `false`
- `blocked`: `true`
- `blocking_reason`: `lifecycle_control_not_implemented`
- `boundary`: `read_only_backoff_status; no_supervised_restart`

The object is static for the current implementation and is copied into the CLI summary view. It does not read state files, inspect processes, start timers, or schedule retries.

## Boundaries

- This change is read-only status metadata.
- It does not implement restart, backoff, scheduler, supervisor, retry timers, or automatic recovery.
- It does not read/write pidfiles or statefiles.
- It does not scan process tables or infer ownership from ports/HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

