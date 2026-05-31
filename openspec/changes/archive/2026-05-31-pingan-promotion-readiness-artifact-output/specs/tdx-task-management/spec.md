## ADDED Requirements

### Requirement: Task management SHALL persist PingAn promotion readiness rollup artifacts on request

The task manager SHALL allow callers to write the read-only PingAn promotion readiness rollup to a caller-provided JSON path.

#### Scenario: Caller writes a rollup artifact

- **WHEN** a caller provides `json_output_path`
- **THEN** the task result SHALL include `promotion_readiness_rollup_artifact`
- **AND** the JSON file SHALL contain the rollup payload and task metadata
- **AND** the artifact metadata SHALL include the written path.

#### Scenario: Caller omits artifact path

- **WHEN** a caller omits `json_output_path`
- **THEN** the task SHALL behave as the existing in-memory read-only rollup
- **AND** it SHALL not write a default artifact file.

#### Scenario: Artifact write failure is explicit

- **WHEN** the requested artifact cannot be written
- **THEN** the task SHALL return `INVALID_REQUEST`
- **AND** it SHALL not execute broker, desktop, trade, report, or catalog workflows.

