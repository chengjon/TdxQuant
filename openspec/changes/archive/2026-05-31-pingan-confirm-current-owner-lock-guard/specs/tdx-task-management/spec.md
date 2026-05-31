## ADDED Requirements

### Requirement: Task confirm-current SHALL forward lifecycle owner-lock guard options
`TdxTaskManager.trade_confirm_current(...)` SHALL accept optional lifecycle owner-lock guard options and forward them to `TdxTradeManager.pingan.confirm_current(...)`.

#### Scenario: Task confirm-current forwards owner-lock guard options
- **WHEN** a caller executes `TdxTaskManager.trade_confirm_current(...)` with lifecycle statefile path, owner token, stale timeout, and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass those values to `TdxTradeManager.pingan.confirm_current(...)`
- **AND** the task MUST NOT perform lifecycle owner-lock acquire/release or write statefile/lock artifacts itself.

#### Scenario: Task confirm-current default dispatch remains unchanged
- **WHEN** a caller executes `TdxTaskManager.trade_confirm_current(...)` without lifecycle owner-lock guard options
- **THEN** the task MUST keep the existing confirm-current manager call shape.
