## ADDED Requirements

### Requirement: Subscription governance reason summary SHALL expose reason map key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.reason_summary.source_key_count` and `status_summary.governance.reason_summary.reason_code_key_count` fields derived from existing reason-summary count maps without changing governance decisions, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Reason summary reports source key count

- **WHEN** `governance.reason_summary.source_counts` contains zero or more source keys
- **THEN** `governance.reason_summary.source_key_count` MUST equal the number of keys in `source_counts`
- **AND** the field MUST be `0` when no advisory reasons exist

#### Scenario: Reason summary reports reason-code key count

- **WHEN** `governance.reason_summary.reason_code_counts` contains zero or more reason-code keys
- **THEN** `governance.reason_summary.reason_code_key_count` MUST equal the number of keys in `reason_code_counts`
- **AND** existing `governance.reason_count`, `source_counts`, and `reason_code_counts` MUST remain available

#### Scenario: Reason key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the reason key-count fields MUST NOT expose full reasons in compact summary view
- **AND** the fields MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, process ownership, or governance policy proof

