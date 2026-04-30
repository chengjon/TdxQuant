## ADDED Requirements

### Requirement: Task management SHALL pass stable desktop trade safety controls through trade tasks
The system SHALL allow stable trade-oriented task workflows to accept and forward the desktop trade safety controls already supported by the stable trade management layer.

#### Scenario: Caller runs trade buy task with safety controls
- **WHEN** a caller executes the stable `trade_buy` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST forward those values into the underlying stable desktop trade management call

#### Scenario: Caller runs trade submit-once task with safety controls
- **WHEN** a caller executes the stable `trade_submit_once` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST forward those values into the underlying stable desktop trade management call

#### Scenario: Caller runs guarded trade buy task with safety controls
- **WHEN** a caller executes the stable `guarded_trade_buy` task workflow with `submission_key` or `max_price`
- **THEN** the task workflow MUST preserve those values through its guarded prechecks and forward them into the underlying stable desktop trade step

### Requirement: Task preset execution SHALL preserve trade safety controls for stable trade tasks
The system SHALL allow preset-driven stable trade task execution to carry the same desktop trade safety controls while still preferring explicit CLI overrides.

#### Scenario: Task run preserves explicit safety-control overrides
- **WHEN** a caller executes `task run --preset ...` for a stable trade-oriented task and also provides explicit `submission_key` or `max_price`
- **THEN** the resolved task workflow MUST receive those explicit values even if the preset defines different defaults
