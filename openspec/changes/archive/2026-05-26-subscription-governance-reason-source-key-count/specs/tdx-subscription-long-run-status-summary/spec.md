## ADDED Requirements

### Requirement: Subscription governance summary SHALL expose reason source key count

Subscription long-run status summaries SHALL include additive `status_summary.governance.reason_source_key_count` derived from the existing top-level `governance.reason_source_counts` map without changing governance decisions, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Governance reason source key count is empty

- **WHEN** no advisory governance reasons exist
- **THEN** `governance.reason_source_counts` MUST remain an empty map
- **AND** `governance.reason_source_key_count` MUST be `0`

#### Scenario: Governance reason source key count reflects source distribution

- **WHEN** advisory governance reasons produce one or more reason-source count-map keys
- **THEN** `governance.reason_source_key_count` MUST equal the number of keys in `governance.reason_source_counts`
- **AND** existing `governance.reason_count`, `governance.reason_source_counts`, and `governance.reason_summary` MUST remain available

#### Scenario: Reason source key count remains advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** `governance.reason_source_key_count` MUST NOT expose full reasons in compact summary view
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the field MUST NOT be treated as health, readiness, PID liveness, process ownership, escalation policy, or governance policy proof

