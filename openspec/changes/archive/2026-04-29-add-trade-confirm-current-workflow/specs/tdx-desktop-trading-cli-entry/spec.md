## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable confirm-current subcommand
The system SHALL expose a stable nested `trade confirm-current` CLI entrypoint for the current-confirm desktop trade workflow.

#### Scenario: Caller uses nested trade confirm-current command
- **WHEN** a caller executes `trade confirm-current`
- **THEN** the CLI MUST dispatch the stable desktop trade confirm-current workflow

#### Scenario: Caller provides current-confirm boundary controls
- **WHEN** a caller executes `trade confirm-current`
- **THEN** the CLI MUST accept confirm/result boundary controls such as `dialog_lookup_mode`, `confirm_timeout`, `result_timeout`, and `close_result_dialog`
- **AND** the resolved workflow MUST receive those values unchanged
