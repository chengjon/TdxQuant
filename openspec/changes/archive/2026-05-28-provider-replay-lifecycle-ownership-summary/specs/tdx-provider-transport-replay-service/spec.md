## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose ownership summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.ownership_summary` metadata that distinguishes current non-ownership from future daemon lifecycle control.

#### Scenario: Detailed status reports no lifecycle ownership

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.ownership_summary.ownership_status` MUST be `not_managed`
- **AND** `lifecycle.ownership_summary.owned_process` MUST be `false`
- **AND** `lifecycle.ownership_summary.state_file_present` MUST be `false`
- **AND** `lifecycle.ownership_summary.state_file_stale` MUST be `false`
- **AND** `lifecycle.ownership_summary.control_allowed` MUST be `false`
- **AND** the summary MUST identify the status source as a configured boundary rather than ownership proof

#### Scenario: Summary view projects lifecycle ownership without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.ownership_summary` MUST match the detailed lifecycle ownership summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior

#### Scenario: Ownership summary remains a boundary declaration

- **WHEN** lifecycle ownership summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof
- **AND** future lifecycle control MUST still require explicit ownership metadata before stop or restart operations can be allowed

