## ADDED Requirements

### Requirement: Task trade audit lookup SHALL provide a stable workflow for resolving single trade audit artifacts
The system SHALL provide a stable task-facing workflow that reads immutable trade-audit artifacts and resolves exact or candidate matches for trade debugging and traceability.

#### Scenario: Caller looks up a single audit by audit id
- **WHEN** a caller provides an `audit_id` that matches one stored audit artifact
- **THEN** the workflow MUST return the matching audit entry summary
- **AND** the workflow MUST include the loaded full audit JSON payload

#### Scenario: Caller looks up audit candidates by contract number or submission key
- **WHEN** a caller provides `contract_no` or `submission_key` instead of `audit_id`
- **THEN** the workflow MUST return matching candidate entries ordered from newest to oldest

#### Scenario: Caller exports trade audit lookup results
- **WHEN** a caller provides output paths for the trade audit lookup workflow
- **THEN** the workflow MUST write the lookup result to structured export artifacts
