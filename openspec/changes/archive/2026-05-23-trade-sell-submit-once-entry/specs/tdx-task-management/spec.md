## ADDED Requirements

### Requirement: Trade submit-once task SHALL route sell side through sell submit-once identity

The task-level submit-once workflow SHALL route explicit sell-side submit-once requests through the dedicated Ping An sell submit-once manager identity.

#### Scenario: Caller runs a sell submit-once task

- **WHEN** a caller runs `trade_submit_once` with `side=sell`
- **THEN** the task MUST call `TdxTradeManager.pingan.sell_submit_once`
- **AND** the task result input MUST preserve `side=sell`
- **AND** refresh and safety controls such as `submission_key` and `max_price` MUST continue to apply

#### Scenario: Caller omits submit-once task side

- **WHEN** a caller runs `trade_submit_once` without a side
- **THEN** the task MUST preserve the existing buy submit-once behavior
