## ADDED Requirements

### Requirement: Task management SHALL expose block read watchlist export as a stable task workflow
The system SHALL expose a stable `block-read-watchlist-export` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can safely export provider-level watchlist snapshots to a local JSON file without composing raw manager calls and file-write logic manually.

#### Scenario: Caller runs block read watchlist export through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read watchlist export workflow through `manager.block_read_watchlist_export(...)`
- **AND** the task workflow MUST delegate snapshot retrieval to `manager.block.read_watchlist_snapshot(...)` rather than reimplementing provider-level snapshot normalization logic

#### Scenario: Caller runs block read watchlist export through task CLI
- **WHEN** a caller invokes `task block-read-watchlist-export`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to manually combine `task block-read-watchlist` with ad hoc file writing

#### Scenario: Task block read watchlist export preserves provider snapshot and appends thin export metadata
- **WHEN** a caller executes the stable block read watchlist export workflow successfully
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST append a thin `data.export` object containing file-output metadata instead of redefining a second block-read-watchlist snapshot schema

#### Scenario: Task block read watchlist export retains snapshot on export failure
- **WHEN** snapshot retrieval succeeds but output-path validation or file writing fails
- **THEN** the returned result MUST remain a failure
- **AND** the result MUST continue to preserve `data.snapshot`
- **AND** the task layer MUST expose only failure-context export metadata instead of success-only file-size or overwrite fields
