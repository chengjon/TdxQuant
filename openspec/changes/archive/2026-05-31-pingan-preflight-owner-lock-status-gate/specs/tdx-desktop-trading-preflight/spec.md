## ADDED Requirements

### Requirement: PingAn trade preflight SHALL optionally report lifecycle owner lock status

The stable PingAn trade preflight workflow SHALL optionally include a read-only lifecycle owner lock status summary when callers provide local owner statefile inputs.

#### Scenario: Caller requests lifecycle owner lock status in preflight

- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` with a lifecycle statefile path and owner token
- **THEN** `promotion_gate_status.lifecycle_owner_lock_status` MUST report a status check for that local owner lock
- **AND** the summary MUST include statefile path, lock path, current owner token, stale status, statefile/lock presence, owner PID diagnostics, `pid_ownership_claimed=false`, and `side_effect_level=none`
- **AND** the preflight workflow MUST NOT acquire or release the owner lock.

#### Scenario: Caller omits lifecycle owner lock inputs

- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` without lifecycle owner lock inputs
- **THEN** `promotion_gate_status.lifecycle_owner_lock_status` MUST report `configured=false`
- **AND** it MUST report `status_check_executed=false`.

### Requirement: PingAn trade preflight SHALL remain non-side-effecting with owner lock status

The stable PingAn trade preflight workflow SHALL keep its read-only behavior even when lifecycle owner lock status is requested.

#### Scenario: Owner lock status preflight does not write lifecycle or trade artifacts

- **WHEN** a caller executes PingAn trade preflight with lifecycle owner lock status inputs
- **THEN** the workflow MUST NOT write the lifecycle owner statefile
- **AND** it MUST NOT write the lifecycle lock file
- **AND** it MUST NOT write last-order state, event log, submission ledger, or trade audit artifacts.
