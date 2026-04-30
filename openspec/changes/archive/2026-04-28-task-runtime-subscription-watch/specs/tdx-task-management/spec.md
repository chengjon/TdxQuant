## ADDED Requirements

### Requirement: Task management SHALL expose runtime subscription watch as a stable task workflow
The system SHALL expose a stable runtime subscription watch workflow through `TdxTaskManager` and the `task` CLI group rather than requiring daily callers to orchestrate subscription sessions manually.

#### Scenario: Caller runs subscription watch through task manager
- **WHEN** a caller constructs `TdxTaskManager`
- **THEN** the caller MUST be able to invoke a stable runtime watch workflow through `manager.subscription_watch(...)`

#### Scenario: Caller runs subscription watch through task CLI
- **WHEN** a caller invokes `task subscription-watch`
- **THEN** the CLI MUST dispatch the workflow through the stable task-management path instead of requiring direct session-level runtime calls
