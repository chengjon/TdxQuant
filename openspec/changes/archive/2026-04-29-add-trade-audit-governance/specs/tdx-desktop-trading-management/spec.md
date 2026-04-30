## ADDED Requirements

### Requirement: Desktop trading management SHALL expose trade-audit target discovery together with existing artifact governance
The system SHALL expose the configured trade-audit artifact target alongside the existing state, event-log, and submission-ledger artifact targets.

#### Scenario: Trade readiness summary includes trade-audit target
- **WHEN** a caller executes a stable trade discovery-style workflow such as health, preflight, or dialog readiness
- **THEN** the returned artifact target summary MUST include the configured trade-audit target path in addition to the existing trade artifact targets

### Requirement: Desktop trading management SHALL preserve audit correlation in persisted artifacts
The system SHALL preserve normalized trade-audit correlation data across the existing state and event artifacts for finalized stable trade workflows.

#### Scenario: Finalized trade writes audit-aware persisted artifacts
- **WHEN** a stable desktop trade workflow finishes through the finalized persistence path
- **THEN** the written last-order state payload MUST include the normalized `trade_audit` summary
- **AND** the appended order-event row MUST include the normalized `trade_audit` summary
