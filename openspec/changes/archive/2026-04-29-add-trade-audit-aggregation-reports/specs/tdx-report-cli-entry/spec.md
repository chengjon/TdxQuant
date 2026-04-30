## ADDED Requirements

### Requirement: Report CLI SHALL expose dedicated trade audit daily and period commands
The system SHALL expose dedicated nested `report audit-daily` and `report audit-period` commands for stable inspection of aggregated desktop trade audit artifacts.

#### Scenario: Caller uses report audit-daily command
- **WHEN** a caller executes a supported trade audit daily report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-daily` command

#### Scenario: Caller uses report audit-period command
- **WHEN** a caller executes a supported trade audit period report workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-period` command
