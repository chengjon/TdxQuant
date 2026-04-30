## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable health subcommand
The system SHALL expose a stable nested `trade health` CLI entrypoint for the read-only desktop trade health workflow.

#### Scenario: Caller uses nested trade health command
- **WHEN** a caller executes `trade health`
- **THEN** the CLI MUST dispatch the stable desktop trade health workflow

#### Scenario: Caller requests HID ping through trade health command
- **WHEN** a caller executes `trade health` with a HID `port`
- **THEN** the CLI MUST accept `port`, `baudrate`, `timeout`, and `pre_delay`
- **AND** the resolved health workflow MUST receive those values unchanged
