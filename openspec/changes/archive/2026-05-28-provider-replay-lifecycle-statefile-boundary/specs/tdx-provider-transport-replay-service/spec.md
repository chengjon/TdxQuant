## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose statefile boundary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.statefile_summary` metadata derived from the optional `lifecycle_state_file` config value.

#### Scenario: Detailed status reports no statefile is configured

- **WHEN** provider replay status is built without `lifecycle_state_file`
- **THEN** `lifecycle.statefile_summary.statefile_status` MUST be `not_configured`
- **AND** `lifecycle.statefile_summary.configured` MUST be `false`
- **AND** `lifecycle.statefile_summary.path_provided` MUST be `false`
- **AND** `lifecycle.statefile_summary.read_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.write_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.present` MUST be `null`
- **AND** `lifecycle.statefile_summary.stale` MUST be `null`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Detailed status reports configured statefile is not inspected

- **WHEN** provider replay status is built with `lifecycle_state_file`
- **THEN** `lifecycle.statefile_summary.statefile_status` MUST be `configured_not_inspected`
- **AND** `lifecycle.statefile_summary.configured` MUST be `true`
- **AND** `lifecycle.statefile_summary.path_provided` MUST be `true`
- **AND** `lifecycle.statefile_summary.read_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.write_attempted` MUST be `false`
- **AND** `lifecycle.statefile_summary.present` MUST be `null`
- **AND** `lifecycle.statefile_summary.stale` MUST be `null`
- **AND** the command MUST NOT read, write, create, delete, lock, or validate the statefile path on disk

#### Scenario: Config-check summary reports statefile boundary without inspection

- **WHEN** a caller requests `provider-replay config-check --view summary` for a config containing `lifecycle_state_file`
- **THEN** `summary_view.lifecycle_state_file_provided` MUST be `true`
- **AND** `summary_view.statefile_inspected` MUST be `false`
- **AND** `summary_view.statefile_written` MUST be `false`
- **AND** `summary_view.daemon_lifecycle_managed` MUST remain `false`
- **AND** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Statefile boundary is non-authoritative

- **WHEN** statefile boundary metadata is present
- **THEN** it MUST NOT be treated as process ownership proof, stale-state proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future lifecycle statefile behavior MUST still require explicit implementation, ownership proof, state schema, stale detection policy, and opt-in control semantics
