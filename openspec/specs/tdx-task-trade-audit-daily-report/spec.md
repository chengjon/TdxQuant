# tdx-task-trade-audit-daily-report Specification

## Purpose
TBD - created by archiving change add-trade-audit-aggregation-reports. Update Purpose after archive.
## Requirements
### Requirement: Task trade audit daily report SHALL provide a stable day-level audit aggregation workflow
The system SHALL provide a stable task-facing workflow that reads immutable trade-audit artifacts, filters entries by local trade date, and returns structured daily aggregation data.

#### Scenario: Caller generates report for the default local trade date
- **WHEN** a caller runs the trade audit daily report workflow without explicitly providing a report date
- **THEN** the workflow MUST generate the report using the current date in the configured local timezone

#### Scenario: Caller generates report for a specific audit date
- **WHEN** a caller provides an explicit report date and timezone
- **THEN** the workflow MUST filter trade-audit entries using that local-date boundary before aggregation

#### Scenario: Caller exports the daily audit report
- **WHEN** a caller provides output paths for the trade audit daily report workflow
- **THEN** the workflow MUST write a structured JSON report and a CSV aggregation view

