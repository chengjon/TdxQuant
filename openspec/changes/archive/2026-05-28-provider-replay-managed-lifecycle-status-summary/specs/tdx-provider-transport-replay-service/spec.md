## MODIFIED Requirements

### Requirement: Provider replay lifecycle status SHALL expose control summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.control_summary` metadata that identifies current lifecycle control availability.

#### Scenario: Configured lifecycle statefile reports managed daemon control surface

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **WHEN** provider replay status is built
- **THEN** `lifecycle.start_stop_managed` MUST be `true`
- **AND** `lifecycle.daemon_managed` MUST be `true`
- **AND** `lifecycle.control_summary.control_status` MUST be `operator_opt_in_available`
- **AND** `lifecycle.control_summary.control_allowed` MUST be `false`
- **AND** `lifecycle.control_summary.available_operations` MUST include `start`, `status`, `stop`, `supervise`, and `restart_backoff`
- **AND** `lifecycle.control_summary.blocked_operations` MUST be empty
- **AND** the summary MUST state that explicit operator invocation remains required.

#### Scenario: Unconfigured lifecycle statefile remains unsupported

- **GIVEN** provider replay config does not include `lifecycle_state_file`
- **WHEN** provider replay status is built
- **THEN** lifecycle control MUST remain unsupported and blocked.

#### Scenario: Managed lifecycle status remains read-only

- **WHEN** managed lifecycle status is reported
- **THEN** status building MUST NOT start, stop, restart, supervise, daemonize, write state files, read process tables, infer ownership from ports, or enable write behavior
- **AND** it MUST NOT be treated as broker availability, workflow readiness, write-capability proof, or real TongDaXin provider lifecycle management.

### Requirement: Provider replay lifecycle status SHALL expose operation summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.operation_summary` metadata that describes current lifecycle operation availability per operation.

#### Scenario: Configured lifecycle statefile reports available managed operations

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **WHEN** provider replay status is built
- **THEN** `lifecycle.operation_summary.operation_count` MUST be `5`
- **AND** `lifecycle.operation_summary.available_count` MUST be `5`
- **AND** `lifecycle.operation_summary.blocked_count` MUST be `0`
- **AND** operations MUST include `start`, `status`, `stop`, `supervise`, and `restart_backoff`
- **AND** each operation MUST be marked `implemented=true` and `status=available`
- **AND** stop and restart/backoff operations MUST continue to declare ownership requirements.

### Requirement: Provider replay lifecycle status SHALL expose supervision summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.supervision_summary` metadata that reports current supervision availability without starting or observing a supervisor.

#### Scenario: Configured lifecycle statefile reports supervisor availability

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **WHEN** provider replay status is built
- **THEN** `lifecycle.supervision_summary.supervision_status` MUST be `operator_opt_in_available`
- **AND** `lifecycle.supervision_summary.supervisor_configured` MUST be `true`
- **AND** `lifecycle.supervision_summary.supervisor_type` MUST be `foreground_cli_supervisor`
- **AND** `lifecycle.supervision_summary.observed_state` MUST be `not_observed`
- **AND** `lifecycle.supervision_summary.control_allowed` MUST be `false`.

### Requirement: Provider replay status summary SHALL expose lifecycle control fields

The provider replay status summary view SHALL include read-only lifecycle ownership/control fields in `summary_view.status_summary` derived only from the already-built lifecycle summary metadata.

#### Scenario: Summary view reports managed lifecycle availability

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.control_supported` MUST be `true`
- **AND** `summary_view.status_summary.managed_operation_count` MUST be greater than `0`
- **AND** `summary_view.status_summary.lifecycle_control_status` MUST match `summary_view.lifecycle.control_summary.control_status`
- **AND** `summary_view.status_summary.lifecycle_supervision_status` MUST match `summary_view.lifecycle.supervision_summary.supervision_status`
- **AND** the command MUST NOT execute lifecycle control or claim provider readiness.

### Requirement: Provider replay CLI SHALL expose non-executing lifecycle control plans

Provider replay CLI SHALL expose a read-only `lifecycle-plan` command that reports the current lifecycle operation plan without executing it.

#### Scenario: Managed lifecycle plan reports available implemented stop with stale ownership blocked

- **GIVEN** provider replay config includes `lifecycle_state_file`
- **AND** the caller requests `provider-replay lifecycle-plan --operation stop --include-statefile-check`
- **AND** the statefile check is valid but stale
- **WHEN** the plan is built
- **THEN** `plan.lifecycle_control_status` MUST be `operator_opt_in_available`
- **AND** `plan.implemented` MUST be `true`
- **AND** `plan.operation_status` MUST remain `blocked`
- **AND** `plan.blocking_reason` MUST identify that the lifecycle statefile is not current
- **AND** `plan.dispatch_executed` MUST be `false`
- **AND** the command MUST NOT execute lifecycle control.
