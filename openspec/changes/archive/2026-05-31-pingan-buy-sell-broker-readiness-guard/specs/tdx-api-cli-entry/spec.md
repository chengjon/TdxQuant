## ADDED Requirements

### Requirement: Trade and task CLI buy/sell SHALL expose broker readiness guard
The stable trade and task CLI buy/sell entrypoints SHALL expose an opt-in broker readiness guard and forward it without changing default behavior.

#### Scenario: Direct trade buy and sell expose broker readiness guard
- **WHEN** a caller runs `trade buy --require-broker-readiness` or `trade sell --require-broker-readiness`
- **THEN** the CLI MUST forward `require_broker_readiness=true` to the stable PingAn buy/sell execution path
- **AND** the CLI MUST NOT manage daemon lifecycle, restart/backoff, retry, recover, or resubmit orders directly.

#### Scenario: Task trade-buy and trade-sell expose broker readiness guard
- **WHEN** a caller runs `task trade-buy --require-broker-readiness` or `task trade-sell --require-broker-readiness`
- **THEN** the CLI MUST forward `require_broker_readiness=true` to `TdxTaskManager.trade_buy(...)` or `TdxTaskManager.trade_sell(...)`
- **AND** the CLI MUST NOT evaluate broker runtime health in the CLI layer.
