# Design: Control rollup summary

## Scope

This change is additive and read-only. It summarizes fields already present in the reconciled `control` payload. It does not acquire locks, read lock contents, signal processes, prove PID liveness, prove ownership, start/stop/restart workers, manage providers, change HTTP routes, change SSE, or change event-stream behavior.

## Field Semantics

`status_summary.control_rollup` SHALL include:

- `control_state`: the reconciled `control.state`, or `unknown` when absent.
- `control_active`: boolean `control.active`.
- `has_control_run_id`: true when `control.run_id` is a non-empty string.
- `has_control_pid`: true when `control.pid` is a positive non-boolean integer.
- `control_reason`: the reconciled `control.reason`, or `null` when absent.
- `has_control_reason`: true when `control.reason` is a non-empty string.
- `stale_process_state`: true when `control.reason` equals `stale_process_state`.
- `startup_persistence_failed`: true when `control.reason` equals `startup_persistence_failed`.

HTTP and CLI summary views SHALL copy `status_summary.control_rollup` from the detailed status summary when present.

## Non-goals

- No lock acquisition, lock inspection, process signaling, restart, backoff, lifecycle, HTTP, SSE, or event-stream execution.
- No PID liveness, process ownership, supervisor ownership, readiness, or provider lifecycle proof.
- No raw `control`, raw `watch_status`, full reasons, or full actions exposure in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.
