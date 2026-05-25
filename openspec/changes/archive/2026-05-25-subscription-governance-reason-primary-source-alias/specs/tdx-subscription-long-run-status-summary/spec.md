## ADDED Requirements

### Requirement: Subscription governance reason summary SHALL expose primary reason source

Subscription long-run status summaries SHALL include additive `governance.reason_summary.primary_reason_source` derived from the first advisory governance reason without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty reason summary has no primary reason source

- **WHEN** no advisory governance reasons are present
- **THEN** `governance.reason_summary.primary_reason_source` MUST be `null`
- **AND** `governance.reason_summary.primary_source` MUST remain available for compatibility

#### Scenario: Advisory reason summary exposes primary reason source

- **WHEN** one or more advisory governance reasons are present
- **THEN** `governance.reason_summary.primary_reason_source` MUST equal `governance.reason_summary.primary_source`
- **AND** aggregate reason counts MUST remain unchanged

#### Scenario: Summary views preserve primary reason source

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance reason summary MUST include `primary_reason_source`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full reason details
