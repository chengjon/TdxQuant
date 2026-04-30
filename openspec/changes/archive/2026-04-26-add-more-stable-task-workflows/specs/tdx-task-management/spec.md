## MODIFIED Requirements

### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above `TdxApiManager` for stable, scenario-oriented daily workflows rather than requiring users to compose raw API calls each time.

#### Scenario: Caller runs a watchlist overview task
- **WHEN** a caller provides a list of stock codes for routine batch overview
- **THEN** the task layer MUST support a stable task that orchestrates batch overview retrieval through manager-backed APIs

#### Scenario: Caller runs a sector formula scan task
- **WHEN** a caller provides a sector/block and a formula name
- **THEN** the task layer MUST support a stable task that first resolves sector constituents and then executes formula scanning through manager-backed APIs
