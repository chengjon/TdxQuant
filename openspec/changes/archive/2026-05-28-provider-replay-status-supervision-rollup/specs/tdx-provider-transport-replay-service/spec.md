## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose supervision rollup fields

Provider replay status summary view SHALL expose compact read-only supervision rollup fields derived from `lifecycle.supervision_summary`.

#### Scenario: Summary status includes supervision scalars

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.status_summary.lifecycle_supervision_status` MUST match `status.lifecycle.supervision_summary.supervision_status`
- **AND** `summary_view.status_summary.lifecycle_supervisor_configured` MUST match `status.lifecycle.supervision_summary.supervisor_configured`
- **AND** `summary_view.status_summary.lifecycle_desired_state` MUST match `status.lifecycle.supervision_summary.desired_state`
- **AND** `summary_view.status_summary.lifecycle_observed_state` MUST match `status.lifecycle.supervision_summary.observed_state`
- **AND** `summary_view.status_summary.lifecycle_process_identity_status` MUST match `status.lifecycle.supervision_summary.process_identity_status`
- **AND** the existing detailed `status` payload and nested `summary_view.lifecycle.supervision_summary` MUST remain available

#### Scenario: Supervision rollup is non-executing

- **WHEN** supervision rollup fields are present
- **THEN** the command MUST NOT start, stop, restart, daemonize, supervise, track pids, read or write state files, inspect process tables, infer ownership from ports, run timers, schedule retries, or enable write behavior
- **AND** the rollup MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
