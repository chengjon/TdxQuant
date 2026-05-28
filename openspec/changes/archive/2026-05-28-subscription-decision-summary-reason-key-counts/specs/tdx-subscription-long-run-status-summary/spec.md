## ADDED Requirements

### Requirement: Subscription governance decision summary SHALL expose reason key counts

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.reason_source_key_count` and `governance.decision_summary.reason_code_key_count` fields derived from existing advisory `governance.reason_summary` key-count data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes reason key counts

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.reason_source_key_count` MUST mirror `governance.reason_summary.source_key_count`
- **AND** `governance.decision_summary.reason_code_key_count` MUST mirror `governance.reason_summary.reason_code_key_count`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes reason key counts

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.reason_source_key_count` MUST mirror `governance.reason_summary.source_key_count`
- **AND** `governance.decision_summary.reason_code_key_count` MUST mirror `governance.reason_summary.reason_code_key_count`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
