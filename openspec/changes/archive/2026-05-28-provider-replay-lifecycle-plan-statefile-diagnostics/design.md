# provider replay lifecycle plan statefile diagnostics design

## Context

`provider-replay lifecycle-plan` is a non-executing plan for lifecycle operations. `provider-replay lifecycle-state-check` explicitly reads a configured lifecycle statefile and reports schema/staleness diagnostics. The plan can expose a compact form of those diagnostics when the caller opts in, but must not make them authoritative.

## Design

Extend parser support:

```text
provider-replay lifecycle-plan --config <path> --operation stop --include-statefile-check [--stale-after-seconds 300] [--view detailed|summary]
```

Default behavior remains unchanged:

- `statefile_check_included=false`
- no statefile file read is attempted

When `--include-statefile-check` is present:

- call `check_provider_replay_lifecycle_statefile(...)`
- embed compact `plan.statefile_diagnostics`
- set `plan.statefile_check_included=true`
- set `plan.statefile_check_status`
- set `plan.statefile_schema_valid`
- set `plan.statefile_provider_id_matches`
- set `plan.statefile_stale`
- keep `plan.control_allowed=false`
- keep `plan.dispatch_executed=false`

Summary view projects the same compact fields.

## Boundaries

- This change is read-only and non-executing.
- The plan only reads the configured statefile when `--include-statefile-check` is explicitly provided.
- The plan never writes or locks statefiles.
- The plan does not start, stop, restart, daemonize, supervise, probe runtime, inspect processes, infer ownership from ports, schedule retries, or enable write behavior.
- Valid statefile diagnostics are not process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry.
