## ADDED Requirements

### Requirement: Task trade period report SHALL provide a stable range-level ledger aggregation workflow
The system SHALL provide a stable task-facing workflow that reads continuous task ledger artifacts, filters entries by local-date range, and returns structured aggregation data for that period.

#### Scenario: Caller generates a single-day period report
- **WHEN** a caller provides only one boundary date
- **THEN** the workflow MUST treat the report period as that single local trade date

#### Scenario: Caller generates a multi-day period report
- **WHEN** a caller provides a start date and an end date
- **THEN** the workflow MUST include all ledger entries whose local dates fall within the inclusive range before aggregation

#### Scenario: Caller exports the period report
- **WHEN** a caller provides output paths for the period report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV daily aggregation view
