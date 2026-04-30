## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable dialog-readiness subcommand
The system SHALL expose a stable nested `trade dialog-readiness` CLI entrypoint for the read-only desktop trade dialog readiness workflow.

#### Scenario: Caller uses nested trade dialog-readiness command
- **WHEN** a caller executes `trade dialog-readiness`
- **THEN** the CLI MUST dispatch the stable desktop trade dialog readiness workflow

#### Scenario: Caller selects dialog target and visibility semantics
- **WHEN** a caller executes `trade dialog-readiness`
- **THEN** the CLI MUST accept a dialog target selector
- **AND** the CLI MUST accept `require_visible`
- **AND** the resolved workflow MUST receive those values unchanged
