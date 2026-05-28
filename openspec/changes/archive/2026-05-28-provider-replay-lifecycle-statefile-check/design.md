# provider replay lifecycle statefile check design

## Context

`lifecycle_state_file` is currently parsed and reported as a non-inspected boundary. That remains true for `status`, `config-check`, and `lifecycle-plan`. The new check command is a distinct opt-in read-only operation whose purpose is to validate statefile shape and freshness without making the file authoritative for daemon control.

## Design

Add CLI parser support:

```text
provider-replay lifecycle-state-check --config <path> [--stale-after-seconds 300] [--view detailed|summary]
```

The handler loads config and calls a provider replay helper that returns:

- `check_status`: `not_configured`, `missing`, `valid`, or `invalid`
- `configured`
- `read_attempted`
- `write_attempted=false`
- `exists`
- `schema_version`
- `schema_valid`
- `provider_id`
- `provider_id_matches`
- `pid`
- `state`
- `updated_at`
- `age_seconds`
- `stale_after_seconds`
- `stale`
- `errors`
- `error_count`
- `control_allowed=false`
- `boundary=read_only_statefile_check; no_lifecycle_control`

The statefile schema version is `tdx.provider_replay.lifecycle_state.v1`. The current accepted shape is intentionally small and future-compatible; extra keys are ignored.

Summary view copies compact status fields only and omits the full error payload.

## Boundaries

- The command reads only the configured lifecycle statefile path and never writes it.
- The command does not start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, lock files, schedule retries, or enable write behavior.
- Valid statefile output is not process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry.
- Future executable lifecycle control still requires explicit implementation, ownership proof, state schema hardening, stale detection policy, locking semantics, and opt-in control semantics.
