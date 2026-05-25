# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

### Requirement: Subscription long-run governance reason summary SHALL expose reason-code counts

The long-run status summary SHALL include an additive `governance.reason_summary.reason_code_counts` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason-code counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_summary.reason_code_counts` MUST be an empty object
- **AND** `governance.reason_summary.count` MUST remain `0`

#### Scenario: Governance manual-review state has reason-code counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.reason_summary.reason_code_counts` MUST count advisory reason strings from `governance.reasons`
- **AND** the count keys MUST be exact advisory reason codes such as `heartbeat:stale`
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views preserve reason-code counts without exposing full reasons

- **WHEN** a compact summary view includes `governance.reason_summary`
- **THEN** `governance.reason_summary.reason_code_counts` MUST remain present
- **AND** the summary view MUST NOT expose raw `governance.reasons` or `governance.actions`

