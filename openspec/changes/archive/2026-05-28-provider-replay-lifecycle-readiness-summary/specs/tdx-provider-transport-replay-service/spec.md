## ADDED Requirements

### Requirement: Provider replay CLI SHALL expose read-only lifecycle readiness summaries

Provider replay CLI SHALL expose a read-only `lifecycle-readiness` command that summarizes current lifecycle control readiness without executing lifecycle control.

#### Scenario: Lifecycle readiness command parses

- **WHEN** a caller parses `provider-replay lifecycle-readiness --config <path>`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the default view MUST be `detailed`
- **AND** statefile diagnostics MUST be opt-in
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed readiness reports blocked control by default

- **WHEN** a caller requests `provider-replay lifecycle-readiness` without statefile diagnostics
- **THEN** `readiness.ready` MUST be `false`
- **AND** `readiness.readiness_status` MUST be `blocked`
- **AND** `readiness.control_allowed` MUST be `false`
- **AND** `readiness.dispatch_executed` MUST be `false`
- **AND** `readiness.statefile_check_included` MUST be `false`
- **AND** `readiness.missing_requirements` MUST include lifecycle controller, owned process identity, supervisor loop, operator opt-in control, and valid lifecycle statefile requirements
- **AND** the command MUST NOT read the configured lifecycle statefile by default

#### Scenario: Detailed readiness can count valid statefile diagnostic prerequisite

- **WHEN** a caller requests `provider-replay lifecycle-readiness --include-statefile-check` for a valid, non-stale, provider-matched statefile
- **THEN** `readiness.statefile_check_included` MUST be `true`
- **AND** `readiness.statefile_check_status` MUST be `valid`
- **AND** `readiness.statefile_schema_valid` MUST be `true`
- **AND** `readiness.statefile_provider_id_matches` MUST be `true`
- **AND** `readiness.statefile_stale` MUST be `false`
- **AND** `readiness.satisfied_requirements` MUST include `valid_lifecycle_statefile`
- **AND** `readiness.ready` MUST still be `false`
- **AND** `readiness.control_allowed` MUST still be `false`

#### Scenario: Summary readiness projects compact blocked state

- **WHEN** a caller requests `provider-replay lifecycle-readiness --include-statefile-check --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-readiness`
- **AND** `summary_view.ready` MUST be `false`
- **AND** `summary_view.readiness_status` MUST be `blocked`
- **AND** `summary_view.control_allowed` MUST be `false`
- **AND** `summary_view.missing_requirement_count` MUST match the detailed readiness
- **AND** `summary_view.statefile_check_status` MUST match the detailed readiness

#### Scenario: Readiness summary is non-authoritative

- **WHEN** lifecycle readiness output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** valid diagnostics MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
