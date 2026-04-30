# tdx-task-trade-audit-period-report Specification

## Purpose
TBD - created by archiving change add-trade-audit-aggregation-reports. Update Purpose after archive.
## Requirements
### Requirement: Task trade audit period report SHALL provide a stable range-level audit aggregation workflow
The system SHALL provide a stable task-facing workflow that reads immutable trade-audit artifacts, filters entries by local-date range, and returns structured aggregation data for that period.

#### Scenario: Caller generates a single-day audit period report
- **WHEN** a caller provides only one boundary date
- **THEN** the workflow MUST treat the report period as that single local trade date

#### Scenario: Caller generates a multi-day audit period report
- **WHEN** a caller provides a start date and an end date
- **THEN** the workflow MUST include all trade-audit entries whose local dates fall within the inclusive range before aggregation

#### Scenario: Caller exports the audit period report
- **WHEN** a caller provides output paths for the trade audit period report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV daily aggregation view

