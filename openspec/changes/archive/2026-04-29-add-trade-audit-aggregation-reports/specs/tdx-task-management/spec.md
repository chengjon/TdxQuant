## ADDED Requirements

### Requirement: Task management SHALL expose trade audit daily and period aggregation as stable workflows
The system SHALL expose stable task-layer workflows for aggregating immutable trade-audit artifacts by local trade date and by inclusive date range.

#### Scenario: Caller runs a trade audit daily report task
- **WHEN** a caller requests a stable daily report workflow for desktop trade audits
- **THEN** the task layer MUST be able to filter audit artifacts by one local date and return structured aggregation data

#### Scenario: Caller runs a trade audit period report task
- **WHEN** a caller requests a stable period report workflow for desktop trade audits
- **THEN** the task layer MUST be able to filter audit artifacts by an inclusive local-date range and return structured aggregation data
