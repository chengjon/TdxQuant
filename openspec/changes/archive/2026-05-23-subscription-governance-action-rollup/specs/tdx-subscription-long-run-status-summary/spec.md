## ADDED Requirements

### Requirement: Subscription long-run governance summary SHALL expose action rollup
The long-run status summary SHALL include an additive `governance.action_summary` object derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty action rollup
- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.count` MUST be `0`
- **AND** `governance.action_summary.primary_action` MUST be `null`
- **AND** `governance.action_summary.severity` MUST be `none`

#### Scenario: Governance manual-review state has action rollup
- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.count` MUST equal the number of `governance.actions`
- **AND** `governance.action_summary.primary_action` MUST equal the first advisory action name
- **AND** `governance.action_summary.primary_reason` MUST equal the first advisory action reason
- **AND** the rollup MUST remain advisory-only
