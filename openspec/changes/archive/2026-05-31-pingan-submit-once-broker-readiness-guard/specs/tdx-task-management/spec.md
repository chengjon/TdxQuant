## ADDED Requirements

### Requirement: Task submit-once SHALL forward broker readiness guard
Task submit-once workflow SHALL accept the broker readiness guard option and forward it to the side-specific PingAn manager submit-once method without evaluating broker health in the task layer.

#### Scenario: Task buy submit-once forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_submit_once(...)` is called with `side=buy` and `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.buy_submit_once(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.

#### Scenario: Task sell submit-once forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_submit_once(...)` is called with `side=sell` and `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.sell_submit_once(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.
