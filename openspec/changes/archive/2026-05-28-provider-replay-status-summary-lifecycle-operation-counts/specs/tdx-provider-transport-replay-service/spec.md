## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose lifecycle operation counts

The provider replay status summary view SHALL include read-only lifecycle operation count fields in `summary_view.status_summary` derived only from the already-built lifecycle operation summary metadata.

#### Scenario: Summary view exposes compact lifecycle operation counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_operation_count` MUST match `summary_view.lifecycle.operation_summary.operation_count`
- **AND** `summary_view.status_summary.lifecycle_available_operation_count` MUST match `summary_view.lifecycle.operation_summary.available_count`
- **AND** `summary_view.status_summary.lifecycle_blocked_operation_count` MUST match `summary_view.lifecycle.operation_summary.blocked_count`
- **AND** `summary_view.status_summary.lifecycle_primary_blocked_operation` MUST identify the first blocked lifecycle operation

#### Scenario: Summary lifecycle operation counts remain read-only

- **WHEN** the summary view exposes lifecycle operation count fields
- **THEN** the detailed `status` payload and `summary_view.lifecycle.operation_summary` MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

