## ADDED Requirements

### Requirement: Guarded trade-buy task SHALL forward lifecycle owner-lock guard options

The guarded PingAn trade-buy task workflow SHALL accept optional lifecycle owner-lock guard options and forward them to the delegated `trade_buy` workflow.

#### Scenario: Guarded trade-buy forwards owner-lock guard options

- **WHEN** a caller executes `TdxTaskManager.guarded_trade_buy(...)` with `require_lifecycle_owner_lock=true`
- **THEN** the guarded workflow MUST pass lifecycle statefile path, lifecycle owner token, stale timeout, and require flag to `TdxTaskManager.trade_buy(...)`
- **AND** it MUST preserve existing guarded prechecks and trade safety controls such as `submission_key`, `max_price`, and `max_snapshot_price`.

### Requirement: Guarded owner-lock forwarding SHALL remain delegated safety evidence

Guarded trade-buy owner-lock forwarding SHALL remain argument forwarding to the delegated trade execution workflow.

#### Scenario: Guarded forwarding remains bounded

- **WHEN** guarded trade-buy receives lifecycle owner-lock guard options
- **THEN** it MUST NOT acquire or release owner locks
- **AND** it MUST NOT write lifecycle statefile/lock artifacts directly
- **AND** it MUST NOT start, stop, restart, kill, supervise, or back off PingAn processes.
