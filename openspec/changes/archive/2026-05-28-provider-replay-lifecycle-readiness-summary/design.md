# provider replay lifecycle readiness summary design

## Context

Provider replay lifecycle control is still unavailable. Existing fields can describe blocked operations, statefile boundaries, statefile diagnostics, and supervision state, but they do not provide a single readiness rollup. This feature provides that rollup without changing any control behavior.

## Design

Add CLI parser support:

```text
provider-replay lifecycle-readiness --config <path> [--include-statefile-check] [--stale-after-seconds 300] [--view detailed|summary]
```

Detailed readiness shape:

- `readiness_status`: `blocked`
- `ready`: `false`
- `control_allowed`: `false`
- `dispatch_executed`: `false`
- `blocking_reason`
- `missing_requirements`
- `missing_requirement_count`
- `satisfied_requirements`
- `satisfied_requirement_count`
- `required_requirement_count`
- `statefile_check_included`
- compact statefile diagnostic fields
- `supervision_status`
- `lifecycle_control_status`
- `boundary`

The readiness builder is static for current lifecycle control. It always includes missing requirements for:

- `lifecycle_controller`
- `owned_process_identity`
- `supervisor_loop`
- `operator_opt_in_control`

If statefile diagnostics are not included or invalid/stale/provider-mismatched, it also keeps `valid_lifecycle_statefile` missing. If a valid, non-stale, provider-matched statefile is explicitly included, that requirement is counted as satisfied, but readiness still remains blocked because the control plane is not implemented.

Summary view projects only compact readiness fields and not the full diagnostic payload.

## Boundaries

- This is read-only readiness metadata.
- It does not start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior.
- `ready=false` and `control_allowed=false` remain invariant for the current implementation.
- A valid statefile can only satisfy one diagnostic prerequisite. It is not process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry.
