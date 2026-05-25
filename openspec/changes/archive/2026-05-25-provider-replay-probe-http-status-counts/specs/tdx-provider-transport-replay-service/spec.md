## ADDED Requirements

### Requirement: Provider replay probe summary SHALL expose requested HTTP status counts

Provider replay status SHALL include additive `runtime.probe_summary.requested_http_status_counts`, a compact count map derived only from requested fixed probe targets' integer `http_status` values, without changing probe execution, replay lifecycle, daemon management, or write behavior.

#### Scenario: No requested HTTP statuses have empty counts

- **WHEN** provider replay status is built without requested probes that have integer HTTP status values
- **THEN** `runtime.probe_summary.requested_http_status_counts` MUST be an empty object
- **AND** no probe operation MUST be executed

#### Scenario: Requested probes are counted by HTTP status

- **WHEN** provider replay status includes requested probes with integer `http_status` values
- **THEN** `runtime.probe_summary.requested_http_status_counts` MUST count each observed HTTP status code
- **AND** map keys MUST be stringified HTTP status codes
- **AND** `not_requested` probes MUST be excluded

#### Scenario: Summary view preserves requested HTTP status counts

- **WHEN** a caller requests `provider-replay status --view summary`
- **AND** the detailed status includes `runtime.probe_summary.requested_http_status_counts`
- **THEN** `summary_view.probe_summary.requested_http_status_counts` MUST mirror the detailed status probe summary
- **AND** the summary view MUST remain an opt-in compact projection, not a daemon-control API
