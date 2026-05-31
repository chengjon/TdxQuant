## ADDED Requirements

### Requirement: Task submit-ready SHALL forward lifecycle owner-lock guard options
`TdxTaskManager.trade_submit_ready(...)` SHALL accept optional lifecycle owner-lock guard options and forward them to `TdxTradeManager.pingan.submit_ready(...)`.

#### Scenario: Task submit-ready forwards owner-lock guard options
- **WHEN** a caller executes `TdxTaskManager.trade_submit_ready(...)` with lifecycle statefile path, owner token, stale timeout, and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass those values to `TdxTradeManager.pingan.submit_ready(...)`
- **AND** the task MUST NOT perform lifecycle owner-lock acquire/release or write statefile/lock artifacts itself.

#### Scenario: Task submit-ready default dispatch remains unchanged
- **WHEN** a caller executes `TdxTaskManager.trade_submit_ready(...)` without lifecycle owner-lock guard options
- **THEN** the task MUST keep the existing submit-ready manager call shape.
