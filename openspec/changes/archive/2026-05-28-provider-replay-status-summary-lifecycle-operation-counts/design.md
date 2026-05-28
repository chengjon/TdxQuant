# provider replay status summary lifecycle operation counts design

## Context

The summary view has detailed lifecycle operation metadata, but compact callers often inspect only `status_summary`. Since all lifecycle operations are currently blocked, the first-screen summary should make that explicit without exposing the full operation matrix.

## Design

In `_build_provider_replay_status_summary_view()`, read `lifecycle.operation_summary` when present and add:

- `lifecycle_operation_count`: `operation_summary.operation_count`
- `lifecycle_available_operation_count`: `operation_summary.available_count`
- `lifecycle_blocked_operation_count`: `operation_summary.blocked_count`
- `lifecycle_primary_blocked_operation`: the first operation in `operation_summary.operations` whose `status` is `blocked`

The projection reads already-built lifecycle metadata only. It does not call probes, inspect processes, or mutate provider replay state.

## Boundaries

- This change is read-only summary projection.
- It does not implement start, stop, restart, backoff, scheduler, or supervisor behavior.
- It does not read/write pidfiles or statefiles.
- It does not scan process tables or infer ownership from ports/HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

