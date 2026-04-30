## ADDED Requirements

### Requirement: Task ledger summary SHALL provide a stable workflow for consuming continuous task ledgers
The system SHALL provide a stable task-facing workflow that reads continuous task ledger artifacts and returns structured summary data for daily inspection and downstream automation.

#### Scenario: Caller reads the default guarded trade ledger
- **WHEN** a caller runs the ledger summary workflow without overriding ledger paths
- **THEN** the workflow MUST resolve the default ledger location from the task profile and return structured summary data

#### Scenario: Caller filters ledger entries
- **WHEN** a caller provides filters such as stock code, contract number, task name, or trade status
- **THEN** the workflow MUST only include matching entries in the returned summary view

#### Scenario: Caller exports the filtered ledger view
- **WHEN** a caller provides output paths for the ledger summary workflow
- **THEN** the workflow MUST write the filtered result set to structured export artifacts
