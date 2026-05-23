## ADDED Requirements

### Requirement: Desktop trading management SHALL expose a dedicated Ping An sell submit-once identity

The desktop trading management layer SHALL expose a dedicated Ping An sell submit-once manager path that preserves existing sell execution behavior while recording submit-once-specific identity.

#### Scenario: Caller runs Ping An sell submit-once through the trade manager

- **WHEN** a caller executes `TdxTradeManager.pingan.sell_submit_once`
- **THEN** the manager MUST reuse the existing Ping An sell desktop execution flow
- **AND** the result metadata MUST record the manager method as `sell_submit_once`
- **AND** idempotency and safety controls such as `submission_key` and `max_price` MUST continue to apply before desktop execution

#### Scenario: Caller inspects sell submit-once boundaries

- **WHEN** a caller uses the dedicated sell submit-once manager path
- **THEN** the system MUST NOT imply a separate `run_pingan_sell_submit_once` desktop primitive exists
- **AND** the boundary MUST remain limited to the existing Ping An sell desktop workflow
