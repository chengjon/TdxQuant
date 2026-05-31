## ADDED Requirements

### Requirement: PingAn confirm-current SHALL honor broker readiness guard
PingAn confirm-current execution SHALL accept an optional broker readiness guard and MUST reject before confirm dialog lookup/click when the guard is explicitly required and broker runtime health fails.

#### Scenario: Confirm-current rejects before dialog lookup when broker readiness is required but unavailable
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called with `require_broker_readiness=true` and PingAn broker runtime health fails
- **THEN** the manager MUST return a failed result containing `broker_readiness_required_status`
- **AND** the manager MUST NOT perform confirm dialog lookup, confirm click, result dialog lookup, or result dialog close behavior.

#### Scenario: Confirm-current preserves default behavior when broker readiness is not required
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called without `require_broker_readiness`
- **THEN** the manager MUST preserve the existing confirm-current boundary workflow
- **AND** the manager MUST NOT require broker runtime health before dialog lookup.
