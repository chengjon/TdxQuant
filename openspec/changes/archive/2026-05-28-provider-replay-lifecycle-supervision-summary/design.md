# provider replay lifecycle supervision summary design

## Context

Provider replay remains a foreground, fixture-backed HTTP replay service. It does not own a child process, write a pidfile/statefile, inspect a process table, or run a supervisor loop. Existing lifecycle fields block start/stop/restart/backoff operations, but callers still need a stable place to read whether supervision exists.

## Design

Add `lifecycle.supervision_summary` with this current shape:

- `supervision_status`: `not_supervised`
- `supervisor_configured`: `false`
- `supervisor_type`: `none`
- `managed_process_count`: `0`
- `active_process_count`: `0`
- `desired_state`: `unmanaged`
- `observed_state`: `not_observed`
- `process_identity_status`: `not_tracked`
- `state_file_status`: `not_configured`
- `pid_status`: `not_tracked`
- `control_allowed`: `false`
- `blocked`: `true`
- `blocking_reason`: `lifecycle_control_not_implemented`
- `boundary`: `read_only_supervision_status; no_supervisor_loop`

The object is static for the current implementation and is copied into the CLI summary view. It does not read/write pidfiles, inspect processes, open sockets, start child processes, or manage retry/restart loops.

## Boundaries

- This change is read-only status metadata.
- It does not implement start, stop, restart, daemonization, supervision, pid tracking, state tracking, process ownership, scheduler behavior, retry timers, or automatic recovery.
- It does not infer runtime ownership from configured ports or HTTP reachability.
- It does not prove readiness, live provider availability, endpoint coverage, broker readiness, workflow readiness, or write capability.
