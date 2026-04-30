## ADDED Requirements

### Requirement: Task management SHALL allow stable trade-audit daily and period workflows to filter by multiple statuses
The system SHALL allow the stable trade-audit daily and period workflows to accept a list of statuses interpreted with OR semantics, in addition to the existing single-status filter.

#### Scenario: Caller runs trade-audit daily report with multiple statuses
- **WHEN** a caller provides more than one status to the stable trade-audit daily report workflow
- **THEN** the workflow MUST return entries whose audit status matches any provided status

#### Scenario: Caller runs trade-audit period report with multiple statuses
- **WHEN** a caller provides more than one status to the stable trade-audit period report workflow
- **THEN** the workflow MUST return entries whose audit status matches any provided status

#### Scenario: Caller mixes single-status and multi-status filters
- **WHEN** a caller provides both the single-status filter and the multi-status filter in the same stable trade-audit workflow call
- **THEN** the workflow MUST reject the request as invalid instead of guessing precedence
