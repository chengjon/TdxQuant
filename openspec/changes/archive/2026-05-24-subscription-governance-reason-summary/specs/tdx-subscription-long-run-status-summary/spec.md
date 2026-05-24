# tdx-subscription-long-run-status-summary Delta

## ADDED Requirements

### Requirement: Subscription long-run governance summary SHALL expose compact reason summary

The long-run status summary SHALL include an additive `governance.reason_summary` object derived from existing advisory `governance.reasons` without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance observe state has empty reason summary

- **WHEN** subscription watch status has no advisory governance reasons
- **THEN** `governance.reason_summary.count` MUST be `0`
- **AND** `governance.reason_summary.primary_reason` MUST be `null`
- **AND** `governance.reason_summary.primary_source` MUST be `null`
- **AND** `governance.reason_summary.source_counts` MUST be an empty object

#### Scenario: Governance manual-review state has primary reason summary

- **WHEN** subscription watch status has advisory governance reasons
- **THEN** `governance.reason_summary.count` MUST equal the number of advisory reasons
- **AND** `governance.reason_summary.primary_reason` MUST equal the first advisory reason
- **AND** `governance.reason_summary.primary_source` MUST equal the first advisory reason source prefix
- **AND** `governance.reason_summary.source_counts` MUST count reason source prefixes

#### Scenario: CLI summary view exposes compact reason summary

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status summary includes `governance.reason_summary`
- **THEN** the CLI summary result MUST include `governance.reason_summary`
- **AND** the CLI summary result MUST NOT include full `governance.reasons` or `governance.actions`
- **AND** the CLI summary request MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes
