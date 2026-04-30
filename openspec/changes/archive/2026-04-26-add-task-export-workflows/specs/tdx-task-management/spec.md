## MODIFIED Requirements

### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above `TdxApiManager` for stable, scenario-oriented daily workflows rather than requiring users to compose raw API calls each time.

#### Scenario: Caller runs a watchlist export task
- **WHEN** a caller provides a list of stock codes for routine batch overview export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed retrieval and writes structured export artifacts

#### Scenario: Caller runs a sector research export task
- **WHEN** a caller provides a sector/block for routine research export
- **THEN** the task layer MUST support a stable task that orchestrates manager-backed sector research and writes structured export artifacts
