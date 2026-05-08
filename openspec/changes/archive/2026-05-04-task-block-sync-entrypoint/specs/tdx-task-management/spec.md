## ADDED Requirements

### Requirement: Task management SHALL expose block sync as a stable task workflow
The system SHALL expose a stable `block-sync` task workflow through `TdxTaskManager` and the `task` CLI group so daily callers can reuse provider-level block synchronization without composing raw manager calls manually.

#### Scenario: Caller runs block sync through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable block sync workflow through `manager.block_sync(...)`
- **AND** the task workflow MUST delegate to `manager.block.sync_watchlist(...)` rather than reimplementing provider-level synchronization logic

#### Scenario: Caller runs block sync through task CLI
- **WHEN** a caller invokes `task block-sync`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring the caller to invoke `api block-sync` directly

#### Scenario: Task block sync preserves provider-level sync summary and attaches task metadata
- **WHEN** a caller executes the stable block sync task workflow
- **THEN** the returned result MUST preserve the provider-level `data.sync`, `data.block_mutation`, and `artifacts` fields
- **AND** the task layer MUST only append standard task metadata and timing metadata instead of redefining a second block-sync result schema
