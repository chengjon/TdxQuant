## Context

`runtime.probe_summary` contains a detailed additive projection of fixed replay-provider probes. Recent slices added `request_summary`, `health_summary`, and bounded error-sample rollups. The remaining usability gap is a compact object that reports the overall probe outcome without requiring clients to inspect many sibling fields.

## Design

Add `runtime.probe_summary.outcome_summary` in `_build_provider_replay_probe_summary()`.

The summary is derived after request and health summaries are computed. It contains only scalar/count/hint fields already present elsewhere in the same `probe_summary`:

- `status`
- `request_coverage_status`
- `total_count`
- `requested_count`
- `healthy_count`
- `failed_count`
- `unhealthy_count`
- `not_requested_count`
- `all_probes_requested`
- `has_failed_probe`
- `has_unhealthy_probe`
- `primary_problem_probe`
- `primary_error_sample_probe`
- `primary_error_sample_status`

`primary_problem_probe` uses the first available failed probe, then unhealthy probe, then primary error-sample probe. No extra probes are requested and no runtime lifecycle behavior changes.

## Non-Goals

- Do not change health classification, error-sample ordering, request coverage rules, or CLI probe execution.
- Do not promote replay status to a live provider readiness guarantee.
- Do not add daemon start/stop, reconnect, scheduler, lifecycle management, write support, or production governance behavior.
