# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

### Requirement: Subscription long-run governance summary SHALL expose reason source counts

The long-run status summary SHALL include an additive `governance.reason_source_counts` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason source counts

- **WHEN** the governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_source_counts` MUST be an empty object
- **AND** `governance.requires_manual_review` MUST remain `false`

#### Scenario: Governance manual-review state has reason source counts

- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.reason_source_counts` MUST count reason prefixes from `governance.reasons`
- **AND** `overall_status:*`, `heartbeat:*`, `watermark:*`, and `reconnect:*` reasons MUST be counted under their respective prefixes
- **AND** the rollup MUST remain advisory-only

#### Scenario: Summary views expose compact reason source counts

- **WHEN** the CLI or HTTP watch status summary view includes governance details
- **THEN** the compact governance view MUST include `reason_source_counts`
- **AND** the compact governance view MUST continue to omit the full `governance.reasons` list
- **AND** `reason_source_counts` MUST remain a derived summary, not a replacement for full governance reasons in the full status payload
