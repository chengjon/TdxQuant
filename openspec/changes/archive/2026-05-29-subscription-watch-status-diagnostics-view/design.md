# Design: Watch-status diagnostics view

## Scope

This change is additive and read-only. It derives a compact `diagnostics` object from the existing summary projection and its rollups. It does not acquire locks, read PID files, signal processes, start/stop/restart workers, manage providers, change subscription execution, change SSE, or change event-stream behavior.

## View Shape

HTTP `view=diagnostics` and CLI `--view diagnostics` SHALL return the same envelope shape as the summary view with:

- `mode`: `diagnostics`
- existing compact `runtime`, `status_summary`, and `governance` projections from the summary view
- a top-level `diagnostics` object

The `diagnostics` object SHALL include:

- `has_control_rollup`
- `has_consistency_rollup`
- `has_reconnect_rollup`
- `has_evaluation_rollup`
- `has_mismatch`
- `requires_manual_review`
- `staleness_evaluated`
- `has_reconnect_failures`
- `has_reconnect_last_error`
- `has_stale_component`
- `has_not_evaluated_component`
- `all_components_evaluated`
- `boundary`

## Non-goals

- No new lifecycle, reconnect, backoff, restart, or supervisor behavior.
- No lock acquisition, lock inspection, PID-file read, PID liveness proof, process ownership proof, readiness proof, or provider lifecycle proof.
- No raw `control`, raw `watch_status`, full reasons, or full actions exposure in diagnostics view.
- No promotion of B-16 or E-09 to `[已实现]`.
