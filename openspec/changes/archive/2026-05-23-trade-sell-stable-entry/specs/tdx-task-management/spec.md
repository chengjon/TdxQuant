## ADDED Requirements

### Requirement: Task management SHALL expose a stable trade sell workflow

The task layer SHALL provide a `trade-sell` workflow that mirrors `trade-buy` for Ping An desktop sell operations.

#### Scenario: Caller runs a trade sell workflow task

- **WHEN** a caller provides a stable desktop trading sell request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated Ping An sell management path
- **AND** the task result MUST preserve the input, refresh result, trade result, artifacts, and result-dialog summary

#### Scenario: Trade sell task aborts on refresh failure

- **WHEN** a trade sell task requests environment refresh and refresh fails
- **THEN** the task MUST return the refresh failure without invoking the sell workflow
