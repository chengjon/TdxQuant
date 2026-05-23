## ADDED Requirements

### Requirement: Subscription long-run status summary SHALL expose advisory governance action hints
The system SHALL include an advisory `governance.actions` list in `status_summary` that turns existing manual-review reasons into machine-readable action hints without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Caller inspects active status without manual-review reasons
- **WHEN** the governance decision is `observe`
- **THEN** `governance.actions` MUST be an empty list
- **AND** the existing advisory-only boundary MUST remain present

#### Scenario: Caller inspects resilience-state manual review
- **WHEN** the governance reasons include an `overall_status:*` reason
- **THEN** `governance.actions` MUST include an advisory action derived from that reason
- **AND** the action MUST NOT trigger reconnect, restart, backoff, or lifecycle behavior

#### Scenario: Caller evaluates stale heartbeat or watermark inputs
- **WHEN** explicit stale thresholds produce `heartbeat:stale` or `watermark:stale` governance reasons
- **THEN** `governance.actions` MUST include one advisory action per stale input
- **AND** the action list MUST NOT add reasons for inputs whose stale thresholds were omitted
