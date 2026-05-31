## ADDED Requirements

### Requirement: PingAn submit-ready SHALL honor lifecycle owner-lock guard
PingAn submit-ready execution SHALL accept optional lifecycle owner-lock guard options and MUST reject before running the HID submit probe when the guard is explicitly required and not satisfied.

#### Scenario: Submit-ready rejects before HID submit probe when owner lock is required but unavailable
- **WHEN** `TdxTradeManager.pingan.submit_ready(...)` is called with `require_lifecycle_owner_lock=true` and no valid owner-lock status can satisfy the requirement
- **THEN** the manager MUST return a failed result containing `lifecycle_owner_lock_required_status`
- **AND** the manager MUST NOT run HID submit probe or confirm dialog lookup behavior.

#### Scenario: Submit-ready keeps default behavior when owner lock is not required
- **WHEN** `TdxTradeManager.pingan.submit_ready(...)` is called without lifecycle owner-lock guard options
- **THEN** the manager MUST preserve the existing submit-ready boundary workflow
- **AND** the manager MUST NOT require lifecycle statefile ownership.
