## ADDED Requirements

### Requirement: Trade submit-once task SHALL expose explicit order side

The task-level submit-once workflow SHALL accept an explicit buy/sell side selector while keeping buy as the default.

#### Scenario: Caller runs a sell submit-once task

- **WHEN** a caller runs the trade submit-once task with `side=sell`
- **THEN** the task MUST route through the existing Ping An sell execution chain
- **AND** the task result input MUST preserve `side=sell`
- **AND** the task MUST continue to apply existing refresh and safety-control handling

#### Scenario: Caller omits submit-once task side

- **WHEN** a caller runs the trade submit-once task without a side
- **THEN** the task MUST preserve the previous buy submit-once behavior
