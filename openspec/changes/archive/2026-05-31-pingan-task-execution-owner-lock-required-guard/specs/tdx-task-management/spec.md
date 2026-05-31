## ADDED Requirements

### Requirement: Task trade workflows SHALL forward lifecycle owner-lock execution guard options

Stable PingAn task trade workflows SHALL accept optional lifecycle owner-lock guard options and forward them to the selected PingAn manager execution method without implementing a separate guard.

#### Scenario: Task trade-buy forwards the opt-in guard

- **WHEN** a caller executes `TdxTaskManager.trade_buy(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTradeManager.pingan.buy(...)`
- **AND** the task MUST preserve existing trade safety controls such as `submission_key` and `max_price`.

#### Scenario: Task trade-sell forwards the opt-in guard

- **WHEN** a caller executes `TdxTaskManager.trade_sell(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTradeManager.pingan.sell(...)`
- **AND** the task MUST preserve existing trade safety controls such as `submission_key` and `max_price`.

#### Scenario: Task trade-submit-once forwards the opt-in guard for both sides

- **WHEN** a caller executes `TdxTaskManager.trade_submit_once(...)` with `side=buy` or `side=sell` and `require_lifecycle_owner_lock=true`
- **THEN** the task MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to the selected buy-submit-once or sell-submit-once PingAn manager method.

### Requirement: Task owner-lock execution guard SHALL remain delegated safety evidence

The task layer SHALL delegate owner-lock execution guard enforcement to the PingAn manager execution methods and SHALL NOT perform lifecycle control itself.

#### Scenario: Task guard forwarding remains bounded

- **WHEN** task trade workflows receive lifecycle owner-lock guard options
- **THEN** the task layer MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.
