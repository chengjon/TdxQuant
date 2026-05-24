# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

### Requirement: Subscription long-run governance action summary SHALL expose severity counts

The long-run status summary SHALL include an additive `governance.action_summary.severity_counts` object derived from existing advisory governance actions without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty severity counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST remain an empty list
- **AND** `governance.action_summary.severity_counts` MUST be an empty object
- **AND** `governance.action_summary.severity` MUST remain `none`

#### Scenario: Governance manual-review state has severity counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.action_summary.severity_counts` MUST count advisory action severities
- **AND** the severity counts MUST be derived from `governance.actions`
- **AND** the rollup MUST remain advisory-only
