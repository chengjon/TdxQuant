## ADDED Requirements

### Requirement: Provider replay lifecycle plans SHALL expose opt-in statefile diagnostics

Provider replay lifecycle plans SHALL optionally include compact read-only lifecycle statefile diagnostics when explicitly requested.

#### Scenario: Lifecycle plan parses opt-in statefile diagnostics flag

- **WHEN** a caller parses `provider-replay lifecycle-plan --config <path> --operation stop --include-statefile-check`
- **THEN** the command MUST be accepted
- **AND** `include_statefile_check` MUST be `true`
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed lifecycle plan includes statefile diagnostics when requested

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop --include-statefile-check`
- **THEN** `plan.statefile_check_included` MUST be `true`
- **AND** `plan.statefile_check_status` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_schema_valid` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_provider_id_matches` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_stale` MUST reflect the read-only statefile check result
- **AND** `plan.statefile_diagnostics.control_allowed` MUST be `false`
- **AND** `plan.dispatch_executed` MUST remain `false`
- **AND** `plan.control_allowed` MUST remain `false`

#### Scenario: Lifecycle plan excludes statefile diagnostics by default

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop` without `--include-statefile-check`
- **THEN** `plan.statefile_check_included` MUST be `false`
- **AND** `plan.statefile_diagnostics` MUST be `null`
- **AND** the command MUST NOT read the configured lifecycle statefile

#### Scenario: Lifecycle plan summary projects statefile diagnostics

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation restart --include-statefile-check --view summary`
- **THEN** `summary_view.statefile_check_included` MUST be `true`
- **AND** `summary_view.statefile_check_status` MUST match the detailed plan
- **AND** `summary_view.statefile_schema_valid` MUST match the detailed plan
- **AND** `summary_view.statefile_provider_id_matches` MUST match the detailed plan
- **AND** `summary_view.statefile_stale` MUST match the detailed plan
- **AND** `summary_view.control_allowed` MUST remain `false`

#### Scenario: Statefile diagnostics remain non-authoritative

- **WHEN** lifecycle plan statefile diagnostics are present
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** valid diagnostics MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
