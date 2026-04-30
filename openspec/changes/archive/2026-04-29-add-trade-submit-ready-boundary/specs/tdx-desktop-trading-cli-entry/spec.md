## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable submit-ready subcommand
The system SHALL expose a stable nested `trade submit-ready` CLI entrypoint for the pre-confirm desktop trade boundary workflow.

#### Scenario: Caller uses nested trade submit-ready command
- **WHEN** a caller executes `trade submit-ready`
- **THEN** the CLI MUST dispatch the stable desktop trade submit-ready workflow

#### Scenario: Caller provides boundary and safety controls to submit-ready
- **WHEN** a caller executes `trade submit-ready`
- **THEN** the CLI MUST accept `max_price`
- **AND** the CLI MUST accept confirm lookup boundary controls such as `dialog_lookup_mode` and `confirm_timeout`
- **AND** the resolved workflow MUST receive those values unchanged
