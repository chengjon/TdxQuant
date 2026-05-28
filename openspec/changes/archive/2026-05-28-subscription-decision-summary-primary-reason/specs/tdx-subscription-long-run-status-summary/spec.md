## ADDED Requirements

### Requirement: Subscription governance decision summary SHALL expose primary reason

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.primary_reason` derived from existing advisory `governance.reason_summary.primary_reason` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes primary reason

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.primary_reason` MUST mirror `governance.reason_summary.primary_reason`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes primary reason

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.primary_reason` MUST mirror `governance.reason_summary.primary_reason`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

