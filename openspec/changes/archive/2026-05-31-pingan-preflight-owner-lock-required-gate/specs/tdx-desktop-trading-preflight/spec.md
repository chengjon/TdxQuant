## ADDED Requirements

### Requirement: PingAn trade preflight SHALL optionally require local lifecycle owner lock ownership

The stable PingAn trade preflight workflow SHALL support an opt-in read-only requirement that blocks preflight success unless the caller-provided lifecycle owner lock is currently owned by the caller token and is not stale.

#### Scenario: Required lifecycle owner lock is satisfied

- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` with lifecycle owner lock inputs and `require_lifecycle_owner_lock=true`
- **AND** the local owner lock status is `owned`, the current owner token matches the caller token, and the lock is not stale
- **THEN** `promotion_gate_status.lifecycle_owner_lock_status` MUST report `required=true`
- **AND** it MUST report `requirement_status=passed`
- **AND** the preflight result MUST NOT fail because of the owner lock requirement.

#### Scenario: Required lifecycle owner lock is missing or mismatched

- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` with `require_lifecycle_owner_lock=true`
- **AND** the local owner lock is missing, stale, released, unknown, or owned by a different token
- **THEN** `promotion_gate_status.lifecycle_owner_lock_status` MUST report `requirement_status=failed`
- **AND** the preflight result MUST be failed-style without submitting an order or acquiring/releasing the lock.
