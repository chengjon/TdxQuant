## ADDED Requirements

### Requirement: Ping An desktop gateway SHALL route submit-once sell through sell submit-once identity

The Ping An desktop gateway SHALL route canonical sell orders submitted in submit-once execution mode through the dedicated sell submit-once manager identity.

#### Scenario: Caller places a submit-once sell order through the gateway

- **WHEN** a caller submits a canonical securities order request with `side=sell` and the Ping An desktop gateway is configured with `execution_mode=submit_once`
- **THEN** the gateway MUST call `TdxTradeManager.pingan.sell_submit_once`
- **AND** the adapter event step MUST remain `pingan_sell_submit_once`
- **AND** the request MUST preserve submission safety controls such as `submission_key`
