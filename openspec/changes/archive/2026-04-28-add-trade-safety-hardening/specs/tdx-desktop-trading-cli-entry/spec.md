## ADDED Requirements

### Requirement: Stable desktop trade CLI entrypoints SHALL expose safety-control arguments
The system SHALL expose stable safety-control arguments on the nested and flat stable desktop trade CLI entrypoints.

#### Scenario: Caller uses nested trade command with safety controls
- **WHEN** a caller executes `trade buy` or `trade submit-once`
- **THEN** the CLI MUST accept `submission_key`
- **AND** the CLI MUST accept `max_price`

#### Scenario: Caller uses flat compatibility command with safety controls
- **WHEN** a caller executes `pingan-buy` or `pingan-buy-submit-once`
- **THEN** the CLI MUST accept the same stable safety-control arguments as the nested trade commands

### Requirement: Trade preset execution SHALL preserve explicit safety-control overrides
The system SHALL allow preset-driven stable desktop trade execution to use preset safety defaults while still preferring explicit CLI overrides.

#### Scenario: Trade run forwards explicit safety controls
- **WHEN** a caller executes `trade run` with explicit safety-control arguments
- **THEN** the resolved stable trade workflow MUST receive those explicit values even if the preset defines different defaults
