## ADDED Requirements

### Requirement: Stable desktop trade workflows SHALL expose normalized trade safety metadata
The system SHALL attach a stable `trade_safety` object to stable desktop trade workflow results so callers can reason about operational risk without parsing free-form messages.

#### Scenario: Successful trade returns normalized safety metadata
- **WHEN** a caller executes a stable desktop trade workflow through `TdxTradeManager`
- **THEN** the result `data` MUST include `trade_safety`
- **AND** `trade_safety` MUST include a stability grade, side-effect grade, submission-key field, and risk-gate summary

### Requirement: Stable desktop trade workflows SHALL preserve an optional submission key
The system SHALL preserve an optional caller-supplied `submission_key` across result payloads and persisted trade artifacts.

#### Scenario: Caller provides submission key
- **WHEN** a caller executes a stable desktop trade workflow with a `submission_key`
- **THEN** the result `data.trade_safety.submission_key` MUST equal the caller value
- **AND** the persisted last-order state payload and append-only event row MUST contain the same key

### Requirement: Stable desktop trade workflows SHALL reject failed pre-trade risk gates before UI side effects
The system SHALL reject invalid requests before any desktop automation side effects execute.

#### Scenario: Invalid order request fails before desktop execution
- **WHEN** a caller submits an invalid stable desktop order request
- **THEN** the workflow MUST return an invalid-request style result
- **AND** the desktop execution routine MUST NOT be called

#### Scenario: Submitted price exceeds caller ceiling
- **WHEN** a caller supplies `max_price` and the requested order price is greater than that ceiling
- **THEN** the workflow MUST return an invalid-request style result
- **AND** the desktop execution routine MUST NOT be called
