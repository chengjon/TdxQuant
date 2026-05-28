## ADDED Requirements

### Requirement: Subscription governance decision summary SHALL expose primary action reason source

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.decision_summary.primary_action_reason_source` derived from existing advisory `governance.action_summary.primary_reason_source` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes primary action reason source

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.decision_summary.primary_action_reason_source` MUST mirror `governance.action_summary.primary_reason_source`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes primary action reason source

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.decision_summary.primary_action_reason_source` MUST mirror `governance.action_summary.primary_reason_source`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

