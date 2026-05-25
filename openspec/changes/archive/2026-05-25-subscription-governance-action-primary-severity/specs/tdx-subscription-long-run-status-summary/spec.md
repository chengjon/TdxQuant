## ADDED Requirements

### Requirement: Subscription governance action summary SHALL expose primary severity

Subscription long-run status summaries SHALL include additive `governance.action_summary.primary_severity` derived from the first advisory governance action severity without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary has no primary severity

- **WHEN** no advisory governance actions are present
- **THEN** `governance.action_summary.primary_severity` MUST be `"none"`
- **AND** action counts MUST remain zero

#### Scenario: Advisory action summary exposes primary severity

- **WHEN** one or more advisory governance actions are present
- **THEN** `governance.action_summary.primary_severity` MUST equal the first action severity
- **AND** aggregate action counts MUST remain unchanged

#### Scenario: Summary views preserve primary severity

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance action summary MUST include `primary_severity`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full action details
