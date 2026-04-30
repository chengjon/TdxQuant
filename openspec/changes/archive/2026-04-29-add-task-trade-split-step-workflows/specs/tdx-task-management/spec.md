## ADDED Requirements

### Requirement: Task management SHALL expose split-step desktop trade workflows as stable task commands
The system SHALL expose stable task-layer commands for the existing desktop trade split-step workflows so daily callers can reuse the confirm boundary without dropping to the lower-level trade namespace.

#### Scenario: Caller runs task trade-submit-ready
- **WHEN** a caller invokes `task trade-submit-ready`
- **THEN** the CLI MUST dispatch the workflow through `TdxTaskManager.trade_submit_ready(...)`

#### Scenario: Caller runs task trade-confirm-current
- **WHEN** a caller invokes `task trade-confirm-current`
- **THEN** the CLI MUST dispatch the workflow through `TdxTaskManager.trade_confirm_current(...)`

### Requirement: Task preset execution SHALL support split-step desktop trade workflows
The system SHALL allow `task run --preset ...` to target the stable split-step desktop trade workflows while preserving explicit CLI overrides.

#### Scenario: Task run executes a submit-ready preset
- **WHEN** a caller executes a named task preset whose target command is `trade-submit-ready`
- **THEN** the system MUST resolve the preset defaults and run the stable submit-ready workflow through the task-management path

#### Scenario: Task run executes a confirm-current preset
- **WHEN** a caller executes a named task preset whose target command is `trade-confirm-current`
- **THEN** the system MUST resolve the preset defaults and run the stable confirm-current workflow through the task-management path

#### Scenario: Confirm-current preset does not require order-entry fields
- **WHEN** a caller executes a named task preset whose target command is `trade-confirm-current`
- **THEN** preset resolution MUST NOT reject the request for missing `port`, `code`, `price`, or `quantity`
- **AND** any explicitly provided boundary arguments MUST still override preset defaults
