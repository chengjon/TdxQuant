## ADDED Requirements

### Requirement: Desktop trading management SHALL preserve trade safety context in persisted artifacts
The system SHALL persist normalized trade safety context into the existing last-order state and append-only event artifacts for stable desktop trading workflows.

#### Scenario: Trade manager writes safety-aware artifacts
- **WHEN** a stable desktop trade workflow finishes through `TdxTradeManager`
- **THEN** the written last-order state payload and append-only event row MUST include the normalized trade safety summary

### Requirement: Desktop trading management SHALL accept caller safety controls for stable buy workflows
The system SHALL allow stable desktop buy workflows to accept caller safety controls without breaking existing production trade flows.

#### Scenario: Caller supplies safety controls to stable desktop buy workflow
- **WHEN** a caller executes a stable desktop buy workflow through the top-level trade manager and supplies `submission_key` or `max_price`
- **THEN** the workflow MUST accept those options
- **AND** existing required trade inputs and production flow behavior MUST remain unchanged
