# provider replay lifecycle control summary design

## Context

The current provider replay lifecycle surface is observational. It can report configured replay capabilities, probe an already-running replay HTTP service when explicitly requested, and expose ownership status as not managed. It cannot safely start, stop, restart, or supervise processes.

## Design

Add `lifecycle.control_summary` with a stable read-only shape:

- `control_status`: `unsupported`
- `control_allowed`: `false`
- `available_operations`: `[]`
- `blocked_operations`: `["start", "stop", "restart", "backoff"]`
- `blocking_reason`: `lifecycle_control_not_implemented`
- `ownership_required`: `true`
- `operator_action_required`: `true`
- `boundary`: `read_only_lifecycle_status; no_control_operations`

The object is static for the current implementation. It does not inspect process state, invoke probes, write files, or mutate daemon state. It is a compatibility point for future lifecycle control commands.

The CLI summary view should deep-copy this object under `summary_view.lifecycle.control_summary`. No new CLI lifecycle subcommand is added.

## Boundaries

- This change is read-only status metadata.
- It does not implement start, stop, restart, backoff, scheduler, or supervisor behavior.
- It does not read or write pidfiles/statefiles.
- It does not scan process tables or infer ownership from ports/HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.

