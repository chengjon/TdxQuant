## ADDED Requirements

### Requirement: Subscription governance action summary SHALL expose primary reason source

Subscription long-run status summaries SHALL include additive `governance.action_summary.primary_reason_source` derived from the first advisory action reason without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Empty action summary has no primary reason source

- **WHEN** no advisory governance actions are present
- **THEN** `governance.action_summary.primary_reason_source` MUST be `null`

#### Scenario: Advisory action summary exposes primary reason source

- **WHEN** advisory governance actions are present
- **THEN** `governance.action_summary.primary_reason_source` MUST equal the parsed source prefix of `governance.action_summary.primary_reason`
- **AND** aggregate action counts MUST remain unchanged

#### Scenario: Summary views preserve primary reason source

- **WHEN** callers request CLI or HTTP subscription watch status summary views
- **THEN** the compact governance action summary MUST include `primary_reason_source`
- **AND** the summary view MUST remain advisory-only and MUST NOT expose full action details
