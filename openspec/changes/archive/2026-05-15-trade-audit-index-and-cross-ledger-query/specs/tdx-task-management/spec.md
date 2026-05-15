## ADDED Requirements

### Requirement: Task management SHALL expose trade audit cross-ledger query as a read-only task
The system SHALL expose the trade audit cross-ledger query through `TdxTaskManager` and the `task` CLI namespace as a read-only workflow. The workflow MUST attach task metadata and MUST NOT mutate trade audit, submission ledger, or task ledger sources.

#### Scenario: Manager-backed query returns task metadata
- **WHEN** a caller invokes the trade audit cross-ledger query through `TdxTaskManager`
- **THEN** the result includes task metadata with the query task name
- **AND** the result includes source paths and query summary metadata

#### Scenario: CLI parses cross-ledger query options
- **WHEN** a caller parses `task trade-audit-cross-ledger-query` with audit, submission ledger, task ledger, filter, cache, and export arguments
- **THEN** those arguments are available on the parsed namespace for dispatch to the manager-backed task
