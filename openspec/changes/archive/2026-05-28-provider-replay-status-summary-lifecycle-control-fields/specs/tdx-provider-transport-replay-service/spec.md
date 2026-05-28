## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose lifecycle control fields

The provider replay status summary view SHALL include read-only lifecycle ownership/control fields in `summary_view.status_summary` derived only from the already-built lifecycle summary metadata.

#### Scenario: Summary view exposes compact lifecycle control posture

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_ownership_status` MUST match `summary_view.lifecycle.ownership_summary.ownership_status`
- **AND** `summary_view.status_summary.lifecycle_owned_process` MUST match `summary_view.lifecycle.ownership_summary.owned_process`
- **AND** `summary_view.status_summary.lifecycle_control_status` MUST match `summary_view.lifecycle.control_summary.control_status`
- **AND** `summary_view.status_summary.lifecycle_blocking_reason` MUST match `summary_view.lifecycle.control_summary.blocking_reason`

#### Scenario: Summary lifecycle fields remain read-only

- **WHEN** the summary view exposes lifecycle control fields
- **THEN** the detailed `status` payload and `summary_view.lifecycle` MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

