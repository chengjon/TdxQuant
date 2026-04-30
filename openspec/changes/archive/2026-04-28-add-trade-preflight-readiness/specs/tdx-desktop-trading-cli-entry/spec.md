## ADDED Requirements

### Requirement: Trade CLI SHALL expose a stable preflight subcommand
The system SHALL expose a stable nested `trade preflight` CLI entrypoint for the read-only desktop trade preflight workflow.

#### Scenario: Caller uses nested trade preflight command
- **WHEN** a caller executes `trade preflight`
- **THEN** the CLI MUST dispatch the stable desktop trade preflight workflow

#### Scenario: Caller provides stable trade safety controls to preflight
- **WHEN** a caller executes `trade preflight` with `submission_key` or `max_price`
- **THEN** the CLI MUST accept those arguments
- **AND** the resolved preflight workflow MUST receive those values unchanged
