## ADDED Requirements

### Requirement: Task preset execution SHALL expose stable split-step desktop trade defaults for daily use
The system SHALL expose stable task presets for the existing split-step desktop trade workflows so daily callers can reuse fixed environment defaults without retyping the full task command.

#### Scenario: Caller lists split-step task presets
- **WHEN** a caller lists task presets after stable split-step desktop trade workflows are available
- **THEN** the preset registry MUST include stable presets for `trade-submit-ready` and `trade-confirm-current`

#### Scenario: Caller runs a split-step task preset
- **WHEN** a caller executes a named task preset whose target command is `trade-submit-ready` or `trade-confirm-current`
- **THEN** the system MUST resolve the preset defaults and run the existing stable task workflow through the task-management path
