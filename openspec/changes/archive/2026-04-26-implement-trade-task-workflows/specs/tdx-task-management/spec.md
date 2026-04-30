## MODIFIED Requirements

### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above manager-level capabilities for stable, scenario-oriented daily workflows rather than requiring users to compose raw calls each time.

#### Scenario: Caller runs a watchlist overview task
- **WHEN** a caller provides a list of stock codes for routine batch overview
- **THEN** the task layer MUST support a stable task that orchestrates batch overview retrieval through manager-backed APIs

#### Scenario: Caller runs a sector formula scan task
- **WHEN** a caller provides a sector/block and a formula name
- **THEN** the task layer MUST support a stable task that first resolves sector constituents and then executes formula scanning through manager-backed APIs

#### Scenario: Caller runs a watchlist export task
- **WHEN** a caller provides a list of stock codes for routine batch overview export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed retrieval and writes structured export artifacts

#### Scenario: Caller runs a sector research export task
- **WHEN** a caller provides a sector/block for routine research export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed sector research and writes structured export artifacts

#### Scenario: Caller runs a trade buy workflow task
- **WHEN** a caller provides a stable desktop trading buy request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path

#### Scenario: Caller runs a trade submit-once workflow task
- **WHEN** a caller provides a stable desktop trading submit-once request through the task layer
- **THEN** the task layer MUST be able to orchestrate optional environment refresh and then invoke the dedicated trade management path
