## ADDED Requirements

### Requirement: Provider replay CLI SHALL expose read-only lifecycle statefile checks

Provider replay CLI SHALL expose a read-only `lifecycle-state-check` command that validates configured lifecycle statefile shape and freshness without granting lifecycle control.

#### Scenario: Lifecycle statefile check command parses

- **WHEN** a caller parses `provider-replay lifecycle-state-check --config <path>`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the default view MUST be `detailed`
- **AND** the default stale threshold MUST be present

#### Scenario: Detailed check reports configured valid stale statefile

- **WHEN** a caller requests `provider-replay lifecycle-state-check` for a configured statefile using schema `tdx.provider_replay.lifecycle_state.v1`
- **THEN** the result MUST include `statefile_check.check_status=valid`
- **AND** `statefile_check.read_attempted` MUST be `true`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** `statefile_check.schema_valid` MUST be `true`
- **AND** `statefile_check.provider_id_matches` MUST be `true`
- **AND** `statefile_check.stale` MUST reflect the configured stale threshold
- **AND** `statefile_check.control_allowed` MUST be `false`

#### Scenario: Detailed check reports missing statefile

- **WHEN** a caller requests `provider-replay lifecycle-state-check` for a configured path that does not exist
- **THEN** `statefile_check.check_status` MUST be `missing`
- **AND** `statefile_check.read_attempted` MUST be `true`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** `statefile_check.exists` MUST be `false`
- **AND** lifecycle control MUST remain disallowed

#### Scenario: Detailed check reports not configured without filesystem IO

- **WHEN** a caller requests `provider-replay lifecycle-state-check` without `lifecycle_state_file`
- **THEN** `statefile_check.check_status` MUST be `not_configured`
- **AND** `statefile_check.read_attempted` MUST be `false`
- **AND** `statefile_check.write_attempted` MUST be `false`
- **AND** lifecycle control MUST remain disallowed

#### Scenario: Summary check projects compact statefile diagnostics

- **WHEN** a caller requests `provider-replay lifecycle-state-check --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-state-check`
- **AND** `summary_view.check_status` MUST match the detailed statefile check
- **AND** `summary_view.schema_valid` MUST match the detailed statefile check
- **AND** `summary_view.provider_id_matches` MUST match the detailed statefile check
- **AND** `summary_view.stale` MUST match the detailed statefile check
- **AND** `summary_view.control_allowed` MUST be `false`

#### Scenario: Statefile check is non-authoritative

- **WHEN** lifecycle statefile check output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, write or lock statefiles, schedule retries, or enable write behavior
- **AND** a valid check MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
