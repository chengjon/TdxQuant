## ADDED Requirements

### Requirement: Task management SHALL preserve read-only workflows through a dedicated task boundary
The task management layer SHALL route selected read-only task workflows through a dedicated read-only task boundary while preserving the existing `TdxTaskManager` public facade and result contracts.

#### Scenario: Caller invokes a read-only task through TdxTaskManager
- **WHEN** a caller invokes a selected read-only task method through `TdxTaskManager`
- **THEN** the task manager MUST return the same task result shape as before the boundary extraction
- **AND** the task manager MUST keep the existing public method name and arguments

#### Scenario: Read-only task boundary does not execute desktop trading workflows
- **WHEN** the read-only task boundary handles a selected read-only workflow
- **THEN** it MUST NOT dispatch desktop trade buy, sell, submit, confirm, broker lifecycle, or guarded trade execution

#### Scenario: Task CLI remains backed by task manager facade
- **WHEN** a caller invokes an existing task or report CLI command for a selected read-only workflow
- **THEN** the CLI MUST continue to dispatch through `TdxTaskManager`
- **AND** the facade MAY delegate to the read-only task boundary internally without changing CLI behavior
