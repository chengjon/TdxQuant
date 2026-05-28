## ADDED Requirements

### Requirement: Provider replay CLI SHALL expose non-executing lifecycle control plans

Provider replay CLI SHALL expose a read-only `lifecycle-plan` command that reports the current blocked plan for lifecycle operations without executing them.

#### Scenario: Lifecycle plan command parses an operation

- **WHEN** a caller parses `provider-replay lifecycle-plan --config <path> --operation stop`
- **THEN** the command MUST be accepted as a provider replay subcommand
- **AND** the parsed operation MUST be `stop`
- **AND** the default view MUST be `detailed`

#### Scenario: Detailed lifecycle plan reports blocked operation without dispatch

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation stop`
- **THEN** the result MUST include `plan.execution_mode=non_executing_lifecycle_plan`
- **AND** `plan.operation` MUST be `stop`
- **AND** `plan.operation_status` MUST be `blocked`
- **AND** `plan.dispatch_executed` MUST be `false`
- **AND** `plan.control_allowed` MUST be `false`
- **AND** `plan.lifecycle_control_status` MUST be `unsupported`
- **AND** `plan.blocking_reason` MUST identify lifecycle control as not implemented
- **AND** `plan.statefile_configured` MUST reflect the config-derived statefile boundary
- **AND** `plan.supervision_status` MUST reflect lifecycle supervision status

#### Scenario: Summary lifecycle plan projects compact blocked state

- **WHEN** a caller requests `provider-replay lifecycle-plan --operation restart --view summary`
- **THEN** `summary_view.mode` MUST be `lifecycle-plan`
- **AND** `summary_view.operation` MUST be `restart`
- **AND** `summary_view.operation_status` MUST be `blocked`
- **AND** `summary_view.dispatch_executed` MUST be `false`
- **AND** `summary_view.control_allowed` MUST be `false`
- **AND** `summary_view.lifecycle_control_status` MUST be `unsupported`
- **AND** `summary_view.blocking_reason` MUST identify lifecycle control as not implemented

#### Scenario: Lifecycle plan is non-executing

- **WHEN** lifecycle plan output is produced
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, probe runtime, inspect process tables, infer ownership from ports, read or write statefiles, schedule retries, or enable write behavior
- **AND** the plan MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
