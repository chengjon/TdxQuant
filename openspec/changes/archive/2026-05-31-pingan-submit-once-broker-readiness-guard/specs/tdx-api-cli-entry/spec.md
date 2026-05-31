## ADDED Requirements

### Requirement: Trade and task CLI submit-once SHALL expose broker readiness guard
The stable trade and task CLI submit-once entrypoints SHALL expose an opt-in broker readiness guard and forward it without changing default behavior.

#### Scenario: Direct trade submit-once exposes broker readiness guard
- **WHEN** a caller runs `trade submit-once --require-broker-readiness`
- **THEN** the CLI MUST forward `require_broker_readiness=true` to the stable submit-once execution path
- **AND** the CLI MUST NOT manage daemon lifecycle, restart/backoff, retry, recover, or resubmit orders directly.

#### Scenario: Task trade-submit-once exposes broker readiness guard
- **WHEN** a caller runs `task trade-submit-once --require-broker-readiness`
- **THEN** the CLI MUST forward `require_broker_readiness=true` to `TdxTaskManager.trade_submit_once(...)`
- **AND** the CLI MUST NOT evaluate broker runtime health in the CLI layer.
