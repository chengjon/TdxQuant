## ADDED Requirements

### Requirement: Task management SHALL expose block read full as a stable task workflow
The system SHALL expose a stable `block-read-full` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can inspect a higher-level diagnostics view above provider-level block watchlist snapshots without composing raw manager calls manually.

#### Scenario: Caller runs block read full through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read full workflow through `manager.block_read_full(...)`
- **AND** the task workflow MUST delegate to `manager.block.read_watchlist_snapshot(...)` rather than issuing a second raw block read

#### Scenario: Caller runs block read full through task CLI
- **WHEN** a caller invokes `task block-read-full`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke lower-level provider commands directly

#### Scenario: Task block read full preserves canonical snapshot and appends diagnostics summary
- **WHEN** a caller executes the stable block read full task workflow and the provider-level snapshot succeeds
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST append task-level `data.read_full` containing diagnostics summary fields derived from the successful snapshot
- **AND** the task layer MUST continue to append only standard task metadata and timing metadata rather than redefining a second provider-level block-read schema

#### Scenario: Task block read full preserves provider failure contract
- **WHEN** a caller executes the stable block read full task workflow and the provider-level snapshot fails
- **THEN** the task layer MUST preserve the provider failure contract and MUST NOT fabricate `data.read_full`
