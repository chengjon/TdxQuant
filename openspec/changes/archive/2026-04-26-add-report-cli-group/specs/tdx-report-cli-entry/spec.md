## ADDED Requirements

### Requirement: Report CLI SHALL provide a dedicated nested report command group
The system SHALL provide a dedicated nested `report` command group for stable ledger and trade-report inspection workflows.

#### Scenario: Caller uses report daily command
- **WHEN** a caller executes a supported daily trade report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report daily` style command

#### Scenario: Caller uses report lookup command
- **WHEN** a caller executes a supported single-report lookup workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report lookup` style command

### Requirement: Report CLI SHALL preserve task-command compatibility during migration
The system SHALL keep existing report-related `task` commands functional while the dedicated `report` group is introduced.

#### Scenario: Existing task report command remains available
- **WHEN** a caller invokes an existing report-related `task` command during the expansion phase
- **THEN** that command MUST remain usable while the dedicated `report` group is being introduced
