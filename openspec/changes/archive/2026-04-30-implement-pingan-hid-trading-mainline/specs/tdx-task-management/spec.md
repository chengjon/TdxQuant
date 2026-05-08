## ADDED Requirements

### Requirement: Task management SHALL expose stable sell-oriented desktop trade workflows
The system SHALL expose stable task-layer workflows for `PingAn` sell execution in parallel with the existing trade buy and trade submit-once workflows.

#### Scenario: Caller runs a trade sell workflow task
- **WHEN** a caller provides a stable desktop trading sell request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path

#### Scenario: Caller runs a trade sell-submit-once workflow task
- **WHEN** a caller provides a stable desktop trading sell request that advances through HID submit and confirmation through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path

### Requirement: Task management SHALL preserve trade safety controls for sell-oriented trade tasks
The system SHALL allow sell-oriented stable trade task workflows to accept and forward the same desktop trade safety controls already supported by existing trade tasks.

#### Scenario: Caller runs trade sell task with safety controls
- **WHEN** a caller executes the stable `trade_sell` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST forward those values into the underlying stable desktop trade management call

#### Scenario: Caller runs trade sell-submit-once task with safety controls
- **WHEN** a caller executes the stable `trade_sell_submit_once` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST preserve those values through its execution flow and forward them into the underlying stable desktop trade management call

### Requirement: Task preset execution SHALL support sell-oriented desktop trade workflows
The system SHALL allow `task run --preset ...` to target stable sell and sell-submit-once workflows while preserving explicit CLI overrides.

#### Scenario: Caller runs a sell task preset
- **WHEN** a caller executes a named task preset whose target command is `trade-sell`
- **THEN** the system MUST resolve the preset defaults and run the stable trade sell workflow through the task-management path

#### Scenario: Caller runs a sell-submit-once task preset
- **WHEN** a caller executes a named task preset whose target command is `trade-sell-submit-once`
- **THEN** the system MUST resolve the preset defaults and run the stable trade sell-submit-once workflow through the task-management path
