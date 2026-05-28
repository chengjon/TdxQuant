## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose control summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.control_summary` metadata that identifies current lifecycle control operations as unavailable.

#### Scenario: Detailed status reports lifecycle control is unsupported

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.control_summary.control_status` MUST be `unsupported`
- **AND** `lifecycle.control_summary.control_allowed` MUST be `false`
- **AND** `lifecycle.control_summary.available_operations` MUST be empty
- **AND** `lifecycle.control_summary.blocked_operations` MUST include `start`, `stop`, `restart`, and `backoff`
- **AND** `lifecycle.control_summary.blocking_reason` MUST identify lifecycle control as not implemented
- **AND** the summary MUST state that ownership proof and operator action are required before future lifecycle control

#### Scenario: Summary view projects lifecycle control without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.control_summary` MUST match the detailed lifecycle control summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Control summary remains a boundary declaration

- **WHEN** lifecycle control summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit implementation and ownership proof before stop or restart operations can be allowed

