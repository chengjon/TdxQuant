## ADDED Requirements

### Requirement: PingAn confirm-current SHALL honor lifecycle owner-lock guard
PingAn confirm-current execution SHALL accept optional lifecycle owner-lock guard options and MUST reject before advancing the current confirmation dialog when the guard is explicitly required and not satisfied.

#### Scenario: Confirm-current rejects before dialog advancement when owner lock is required but unavailable
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called with `require_lifecycle_owner_lock=true` and no valid owner-lock status can satisfy the requirement
- **THEN** the manager MUST return a failed result containing `lifecycle_owner_lock_required_status`
- **AND** the manager MUST NOT run confirm dialog lookup or click behavior

#### Scenario: Confirm-current keeps default behavior when owner lock is not required
- **WHEN** `TdxTradeManager.pingan.confirm_current(...)` is called without lifecycle owner-lock guard options
- **THEN** the manager MUST preserve the existing confirm-current dialog boundary workflow
- **AND** the manager MUST NOT require lifecycle statefile ownership.
