## ADDED Requirements

### Requirement: PingAn buy and sell SHALL honor broker readiness guard
PingAn buy and sell desktop execution SHALL accept an optional broker readiness guard and MUST reject before buy/sell desktop automation when the guard is explicitly required and broker runtime health fails.

#### Scenario: Buy rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.buy(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the buy desktop automation path.

#### Scenario: Sell rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.sell(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the sell desktop automation path.

#### Scenario: Buy and sell preserve default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.buy(...)` or `TdxTradeManager.pingan.sell(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing buy/sell risk-gate and desktop automation behavior
- **AND** the manager MUST NOT require broker runtime health before desktop dispatch.
