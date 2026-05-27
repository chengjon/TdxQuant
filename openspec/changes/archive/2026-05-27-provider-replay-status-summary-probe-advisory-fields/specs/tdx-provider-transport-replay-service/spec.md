## ADDED Requirements

### Requirement: Provider replay status summary SHALL expose probe advisory fields

The provider replay status summary view SHALL include read-only probe advisory fields in `summary_view.status_summary` derived only from the already-built `runtime.probe_summary`.

#### Scenario: Summary view exposes compact probe advisory posture

- **WHEN** a caller requests `provider-replay status --view summary` with explicit probe flags
- **THEN** `summary_view.status_summary.probe_status` MUST match `runtime.probe_summary.advisory_summary.status`
- **AND** `summary_view.status_summary.probe_request_coverage_status` MUST match `runtime.probe_summary.advisory_summary.request_coverage_status`
- **AND** `summary_view.status_summary.has_problem_probe` MUST match `runtime.probe_summary.advisory_summary.has_problem_probe`
- **AND** `summary_view.status_summary.primary_problem_probe` MUST match `runtime.probe_summary.advisory_summary.primary_problem_probe`

#### Scenario: Summary view probe advisory fields remain read-only

- **WHEN** the summary view exposes probe advisory fields
- **THEN** the detailed `status` payload and copied `probe_summary` MUST remain available
- **AND** the command MUST NOT execute additional probes, start sockets beyond explicitly requested probes, manage daemon lifecycle, schedule supervision, or enable write behavior
- **AND** the fields MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, or write-capability proof

