## ADDED Requirements

### Requirement: Stable desktop trading SHALL expose a read-only request preflight workflow
The system SHALL expose a stable non-side-effecting preflight workflow for one concrete Ping An desktop trade request.

#### Scenario: Caller runs stable Ping An trade preflight
- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` with the requested trade inputs
- **THEN** the result MUST include a structured preflight summary for that concrete trade request
- **AND** the summary MUST include named checks for broker/runtime readiness, buy-page detection, order-request risk gate, and HID path status

### Requirement: Stable desktop trading preflight SHALL evaluate submission-key readiness without side effects
The system SHALL evaluate stable submission-key idempotency semantics during preflight without performing any desktop execution.

#### Scenario: Caller provides submission key during preflight
- **WHEN** a caller executes the stable trade preflight workflow with a `submission_key`
- **THEN** the preflight summary MUST include the idempotency outcome for that key and normalized request

#### Scenario: Preflight detects conflicting submission key
- **WHEN** a caller executes the stable trade preflight workflow with a `submission_key` that conflicts with a previously recorded side-effecting request
- **THEN** the preflight workflow MUST return a failed-style result
- **AND** the preflight summary MUST mark the idempotency check as failed

### Requirement: Stable desktop trading preflight SHALL remain non-side-effecting
The system SHALL keep the stable trade preflight workflow read-only.

#### Scenario: Trade preflight does not write execution artifacts
- **WHEN** a caller executes the stable trade preflight workflow
- **THEN** the workflow MUST NOT write last-order state
- **AND** it MUST NOT append an order event row
- **AND** it MUST NOT append a submission-ledger row
