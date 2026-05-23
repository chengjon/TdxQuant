## ADDED Requirements

### Requirement: Subscription long-run governance summary SHALL expose a manual-review boolean
The long-run status summary SHALL include `governance.requires_manual_review` as an additive boolean derived from the existing advisory governance decision without changing reconnect, backoff, restart, lifecycle, or event-stream behavior.

#### Scenario: Caller inspects observe posture
- **WHEN** the governance decision is `observe`
- **THEN** `governance.requires_manual_review` MUST be `false`
- **AND** existing `governance.actions` MUST remain an empty list

#### Scenario: Caller inspects manual-review posture
- **WHEN** the governance decision is `manual_review`
- **THEN** `governance.requires_manual_review` MUST be `true`
- **AND** existing governance reasons and actions MUST remain available
- **AND** the flag MUST NOT trigger reconnect, backoff, restart, lifecycle, or event-stream behavior
