## ADDED Requirements

### Requirement: Confirm-current CLI SHALL expose broker readiness guard
The stable PingAn confirm-current CLI entrypoints SHALL accept a broker readiness guard option and forward it to the PingAn manager without managing the PingAn process lifecycle.

#### Scenario: Trade confirm-current CLI forwards broker readiness guard
- **WHEN** a caller runs `trade confirm-current --require-broker-readiness`
- **THEN** the CLI MUST pass `require_broker_readiness=true` to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** the CLI MUST NOT start, stop, restart, supervise, retry, recover, or resubmit through this option.

#### Scenario: Task confirm-current CLI forwards broker readiness guard
- **WHEN** a caller runs `task trade-confirm-current --require-broker-readiness`
- **THEN** the CLI MUST pass `require_broker_readiness=true` to `TdxTaskManager.trade_confirm_current(...)`
- **AND** the CLI MUST keep default confirm-current dispatch unchanged when the option is omitted.
