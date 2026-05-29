# Design: Status consistency rollup

## Scope

This change is additive and read-only. It summarizes fields already present in `control` and `watch_status`. It does not acquire locks, read lock contents, read PID files, signal processes, prove PID liveness, prove ownership, start/stop/restart workers, manage providers, change HTTP routes, change SSE, or change event-stream behavior.

## Field Semantics

`status_summary.consistency_rollup` SHALL include:

- `control_state`: `control.state`, or `unknown` when absent.
- `watch_state`: `watch_status.state`, or `null` when absent.
- `has_watch_status`: true when `watch_status` is a non-empty object.
- `has_control_run_id`: true when `control.run_id` is a non-empty string.
- `has_watch_run_id`: true when `watch_status.run_id` is a non-empty string.
- `run_id_match`: true/false when both run IDs are present, otherwise `null`.
- `state_match`: true/false when both states are present, otherwise `null`.
- `has_control_pid`: true when `control.pid` is a positive non-boolean integer.
- `has_mismatch`: true when either comparable state or comparable run ID is explicitly mismatched.

HTTP and CLI summary views SHALL copy `status_summary.consistency_rollup` from the detailed status summary when present.

## Non-goals

- No lock acquisition, lock inspection, PID-file read, process signaling, restart, backoff, lifecycle, HTTP, SSE, or event-stream execution.
- No PID liveness, process ownership, supervisor ownership, readiness, or provider lifecycle proof.
- No raw `control`, raw `watch_status`, full reasons, or full actions exposure in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.
