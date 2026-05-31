## ADDED Requirements

### Requirement: Task run CLI SHALL accept lifecycle owner-lock guard overrides

The stable `task run` CLI SHALL accept lifecycle owner-lock guard arguments for preset-driven PingAn trade task execution.

#### Scenario: Task run parses owner-lock guard overrides

- **WHEN** a caller parses `task run --preset <trade-preset> --require-lifecycle-owner-lock`
- **THEN** the parsed arguments MUST include lifecycle statefile path, lifecycle owner token, stale timeout, and require flag fields.

#### Scenario: Task run CLI override wins over preset value

- **WHEN** a task preset supplies lifecycle owner-lock guard options
- **AND** the caller supplies lifecycle owner-lock guard CLI overrides
- **THEN** the resolved task namespace MUST use the explicit CLI override values.

### Requirement: Task run dispatch SHALL forward resolved owner-lock guard options

Task preset execution SHALL forward resolved lifecycle owner-lock guard options to the selected task trade workflow.

#### Scenario: Task run forwards guard options to trade-buy

- **WHEN** `task run` resolves a preset whose command is `trade-buy`
- **THEN** dispatch MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTaskManager.trade_buy(...)`.

#### Scenario: Task run forwards guard options to trade-submit-once

- **WHEN** `task run` resolves a preset whose command is `trade-submit-once`
- **THEN** dispatch MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTaskManager.trade_submit_once(...)` while preserving explicit side selection.
