## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose failed status counts

Provider replay status SHALL include additive `runtime.probe_summary.failed_status_counts`, a compact count map derived only from requested fixed probe targets whose normalized status is not `healthy`, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested failures have empty failed status counts

- **WHEN** provider replay status is built without requested failed probes
- **THEN** `runtime.probe_summary.failed_status_counts` MUST be an empty object
- **AND** existing requested, healthy, failed, unhealthy, and not-requested target lists MUST remain present

#### Scenario: Degraded requested probes are counted by failed status

- **WHEN** provider replay status includes a requested probe whose status is not `healthy`
- **THEN** `runtime.probe_summary.failed_status_counts` MUST count that requested probe status
- **AND** `runtime.probe_summary.requested_status_counts` MUST continue counting all requested probe statuses
- **AND** the status operation MUST remain read-only and MUST NOT manage daemon lifecycle

#### Scenario: Summary view preserves failed status counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.failed_status_counts`
- **THEN** `summary_view.probe_summary.failed_status_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API
