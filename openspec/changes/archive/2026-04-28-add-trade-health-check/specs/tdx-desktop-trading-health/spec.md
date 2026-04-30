## ADDED Requirements

### Requirement: Stable desktop trading SHALL expose a read-only health workflow
The system SHALL expose a stable non-side-effecting broker/runtime health workflow through the stable desktop trade management surface.

#### Scenario: Caller runs stable Ping An trade health workflow
- **WHEN** a caller executes `TdxTradeManager.pingan.health(...)`
- **THEN** the result MUST include a structured health summary for the stable trade path
- **AND** that summary MUST include broker/runtime readiness details

#### Scenario: Caller requests HID ping during trade health
- **WHEN** a caller executes the stable trade health workflow and provides a HID `port`
- **THEN** the workflow MUST attempt a HID bridge ping using the provided serial settings
- **AND** the structured health summary MUST include the HID ping outcome as a separate named check

### Requirement: Stable desktop trading health SHALL remain non-side-effecting
The system SHALL keep the stable trade health workflow read-only.

#### Scenario: Trade health does not write execution artifacts
- **WHEN** a caller executes the stable trade health workflow
- **THEN** the workflow MUST NOT write last-order state
- **AND** it MUST NOT append an order event row
- **AND** it MUST NOT append a submission-ledger row
