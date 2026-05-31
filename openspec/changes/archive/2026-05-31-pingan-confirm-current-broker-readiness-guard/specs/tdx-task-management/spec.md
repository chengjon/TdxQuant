## ADDED Requirements

### Requirement: Task confirm-current SHALL forward broker readiness guard
Task confirm-current SHALL accept the broker readiness guard option and forward it to the PingAn manager confirm-current method without evaluating broker health in the task layer.

#### Scenario: Task confirm-current forwards broker readiness guard
- **WHEN** `TdxTaskManager.trade_confirm_current(...)` is called with `require_broker_readiness=true`
- **THEN** it MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** it MUST NOT start, stop, restart, supervise, retry, recover, or resubmit orders directly.
