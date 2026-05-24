## ADDED Requirements

### Requirement: Subscription long-run governance summary SHALL expose detailed reason count

The detailed subscription watch status summary SHALL include an additive read-only `governance.reason_count` scalar derived from the existing advisory `governance.reasons` list without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Detailed observe governance has zero reason count

- **WHEN** the detailed status summary governance decision is `observe`
- **THEN** `governance.reasons` MUST remain an empty list
- **AND** `governance.reason_count` MUST be `0`
- **AND** `governance.requires_manual_review` MUST remain `false`

#### Scenario: Detailed manual-review governance counts reasons

- **WHEN** the detailed status summary governance decision is `manual_review`
- **THEN** `governance.reason_count` MUST equal the length of `governance.reasons`
- **AND** `governance.reason_count` MUST remain a derived scalar, not a replacement for the detailed reasons list
- **AND** the rollup MUST remain advisory-only
