## ADDED Requirements

### Requirement: Report CLI SHALL expose a dedicated trade audit lookup command
The system SHALL expose a dedicated nested `report audit-lookup` command for stable inspection of immutable desktop trade audit artifacts.

#### Scenario: Caller uses report audit-lookup command
- **WHEN** a caller executes a supported trade audit lookup workflow through the CLI
- **THEN** the system MUST expose that workflow through a nested `report audit-lookup` command
