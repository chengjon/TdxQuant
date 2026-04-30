## ADDED Requirements

### Requirement: Task management SHALL expose trade audit lookup as a stable task workflow
The system SHALL expose a stable task-layer workflow for resolving immutable trade-audit artifacts without requiring callers to inspect runtime directories manually.

#### Scenario: Caller runs a trade audit lookup task
- **WHEN** a caller requests a stable task workflow for locating one or more desktop trade audit artifacts
- **THEN** the task layer MUST be able to scan audit artifacts, apply filters, and return a structured lookup result
