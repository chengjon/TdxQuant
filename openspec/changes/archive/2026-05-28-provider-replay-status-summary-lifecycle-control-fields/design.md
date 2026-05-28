# provider replay status summary lifecycle control fields design

## Context

The summary view has two layers:

- `summary_view.lifecycle`: structured lifecycle details, now including ownership/control summaries.
- `summary_view.status_summary`: compact first-screen status.

The latter should expose enough lifecycle boundary signal that callers do not confuse replay status/probe availability with lifecycle control support.

## Design

In `_build_provider_replay_status_summary_view()`, read:

- `lifecycle.ownership_summary`
- `lifecycle.control_summary`

Then add these fields to `status_summary`:

- `lifecycle_ownership_status`: ownership summary `ownership_status`
- `lifecycle_owned_process`: ownership summary `owned_process`
- `lifecycle_control_status`: control summary `control_status`
- `lifecycle_blocking_reason`: control summary `blocking_reason`

The projection reads already-built lifecycle metadata only. It does not call probes, inspect processes, or mutate provider replay state.

## Boundaries

- This change is read-only summary projection.
- It does not implement start, stop, restart, backoff, scheduler, or supervisor behavior.
- It does not read/write pidfiles or statefiles.
- It does not scan process tables or infer ownership from ports/HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

