## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose operation summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.operation_summary` metadata that describes current lifecycle operation availability per operation.

#### Scenario: Detailed status reports all lifecycle operations blocked

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.operation_summary.operation_count` MUST be `4`
- **AND** `lifecycle.operation_summary.available_count` MUST be `0`
- **AND** `lifecycle.operation_summary.blocked_count` MUST be `4`
- **AND** `lifecycle.operation_summary.operations` MUST include entries for `start`, `stop`, `restart`, and `backoff`
- **AND** each current operation entry MUST report `status=blocked`, `implemented=false`, and `blocking_reason=lifecycle_control_not_implemented`

#### Scenario: Summary view projects lifecycle operation summary without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.operation_summary` MUST match the detailed lifecycle operation summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Operation summary remains a boundary declaration

- **WHEN** lifecycle operation summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit implementation and ownership proof where required before operations can be allowed

