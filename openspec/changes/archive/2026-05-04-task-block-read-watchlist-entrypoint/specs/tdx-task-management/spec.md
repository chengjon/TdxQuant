## ADDED Requirements

### Requirement: Task management SHALL expose block read watchlist as a stable task workflow
The system SHALL expose a stable `block-read-watchlist` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can reuse provider-level watchlist snapshot reads without composing raw manager calls manually.

#### Scenario: Caller runs block read watchlist through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block read watchlist workflow through `manager.block_read_watchlist(...)`
- **AND** the task workflow MUST delegate to `manager.block.read_watchlist_snapshot(...)` rather than reimplementing provider-level snapshot normalization logic

#### Scenario: Caller runs block read watchlist through task CLI
- **WHEN** a caller invokes `task block-read-watchlist`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke `api block-read-watchlist` directly

#### Scenario: Task block read watchlist preserves provider-level snapshot and attaches task metadata
- **WHEN** a caller executes the stable block read watchlist task workflow
- **THEN** the returned result MUST preserve the provider-level `data.snapshot`, `artifacts`, and `warnings` fields
- **AND** the task layer MUST only append standard task metadata and timing metadata instead of redefining a second block-read-watchlist result schema
