## ADDED Requirements

### Requirement: Command catalog SHALL expose block watchlist export task entries once the preset is stable
The system SHALL expose stable catalog entries for preset-backed block watchlist export task workflows once those presets are available.

#### Scenario: Caller lists block watchlist export catalog entries
- **WHEN** a caller lists catalog entries after the stable `export-zxg-watchlist` task preset is available
- **THEN** the catalog MUST include a task-source entry mapped to that preset

#### Scenario: Caller plans a block watchlist export catalog entry
- **WHEN** a caller executes `catalog plan --entry export-zxg-watchlist`
- **THEN** the system MUST resolve the existing preset-backed task namespace without executing the task workflow

#### Scenario: Caller runs a block watchlist export catalog entry
- **WHEN** a caller executes `catalog run --entry export-zxg-watchlist`
- **THEN** the system MUST dispatch through the existing task-preset workflow instead of inventing a second execution path
