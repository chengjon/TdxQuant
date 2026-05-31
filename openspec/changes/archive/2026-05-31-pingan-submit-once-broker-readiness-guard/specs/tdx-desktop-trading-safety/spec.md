## ADDED Requirements

### Requirement: PingAn submit-once SHALL honor broker readiness guard
PingAn submit-once desktop execution SHALL accept an optional broker readiness guard and MUST reject before submit-once desktop automation when the guard is explicitly required and broker runtime health fails.

#### Scenario: Buy submit-once rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.buy_submit_once(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the buy submit-once desktop automation path.

#### Scenario: Sell submit-once rejects before desktop automation when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.sell_submit_once(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT call the sell submit-once desktop automation path.

#### Scenario: Submit-once preserves default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.buy_submit_once(...)` or `sell_submit_once(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing submit-once risk-gate and desktop automation behavior
- **AND** the manager MUST NOT require broker runtime health before desktop dispatch.
