## ADDED Requirements

### Requirement: Subscription long-run governance action summary SHALL expose action reason-source counts

The long-run status summary SHALL include an additive `governance.action_summary.reason_source_counts` object derived from existing advisory governance action reasons without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action reason-source counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.reason_source_counts` MUST be an empty object
- **AND** `governance.action_summary.primary_action` MUST remain `null`

#### Scenario: Governance manual-review state has action reason-source counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.reason_source_counts` MUST count source prefixes from advisory action `reason` values
- **AND** the action reason-source counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve action reason-source counts without exposing full actions

- **WHEN** a caller requests the CLI or HTTP subscription watch status summary view
- **THEN** the summary view MUST include `governance.action_summary.reason_source_counts`
- **AND** the summary view MUST NOT include the full `governance.actions` list
- **AND** the summary view MUST remain a read-only projection
