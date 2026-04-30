## MODIFIED Requirements

### Requirement: Task management SHALL provide a stable scenario-oriented entry layer above API manager
The system SHALL define a task layer above `TdxApiManager` for stable, scenario-oriented daily workflows rather than requiring users to compose raw API calls each time.

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

#### Scenario: Caller runs a guarded trade buy workflow task
- **WHEN** a caller provides a protected desktop trading buy request with precheck constraints through the task layer
- **THEN** the task layer MUST be able to run manager-backed prechecks before invoking the trade workflow and writing a structured task report

#### Scenario: Guarded trade buy includes formula precheck
- **WHEN** a caller provides a formula constraint for the guarded trade buy workflow
- **THEN** the task layer MUST be able to execute a manager-backed formula precheck before allowing the trade workflow to proceed

#### Scenario: Guarded trade buy appends to task ledger
- **WHEN** a guarded trade buy workflow completes with report artifacts
- **THEN** the task layer MUST be able to append summary entries to continuous ledger artifacts

#### Scenario: Caller runs a ledger summary task
- **WHEN** a caller requests a stable task workflow for inspecting continuous task ledger records
- **THEN** the task layer MUST be able to read ledger artifacts, apply filters, and return a structured summary view

#### Scenario: Caller runs a daily trade report task
- **WHEN** a caller requests a stable task workflow for daily aggregation of trade ledger records
- **THEN** the task layer MUST be able to filter ledger records by local trade date and return a structured aggregated report

#### Scenario: Caller runs a trade report lookup task
- **WHEN** a caller requests a stable task workflow for locating a single trade report from ledger records
- **THEN** the task layer MUST be able to resolve matching ledger entries and linked report artifacts
