## ADDED Requirements

### Requirement: Task buy and sell SHALL forward broker readiness guard
Task buy and sell workflows SHALL accept the broker readiness guard option and forward it to the PingAn manager buy/sell methods without evaluating broker health in the task layer.

#### Scenario: Task buy forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_buy(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.buy(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

#### Scenario: Task sell forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_sell(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.sell(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.
