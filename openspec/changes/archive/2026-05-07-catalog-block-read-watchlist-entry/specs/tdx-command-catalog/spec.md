## ADDED Requirements

### Requirement: Command catalog SHALL expose block read watchlist task entries once the preset is stable
The system SHALL expose stable catalog entries for preset-backed block read watchlist snapshot task workflows once those presets are available.

#### Scenario: Caller lists block read watchlist catalog entries
- **WHEN** a caller lists catalog entries after the stable `read-zxg-watchlist` task preset is available
- **THEN** the catalog MUST include a task-source entry mapped to that preset

#### Scenario: Caller plans a block read watchlist catalog entry
- **WHEN** a caller executes `catalog plan --entry read-zxg-watchlist`
- **THEN** the system MUST resolve the existing preset-backed task namespace without executing the task workflow

#### Scenario: Caller runs a block read watchlist catalog entry
- **WHEN** a caller executes `catalog run --entry read-zxg-watchlist`
- **THEN** the system MUST dispatch through the existing task-preset workflow instead of inventing a second execution path
