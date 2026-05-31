## ADDED Requirements

### Requirement: Trade preflight CLI SHALL accept lifecycle owner lock requirement flag

The stable `trade preflight` CLI SHALL accept an opt-in flag requiring local PingAn lifecycle owner lock ownership during read-only preflight.

#### Scenario: Caller requires lifecycle owner lock during trade preflight

- **WHEN** a caller executes `trade preflight --require-lifecycle-owner-lock` with lifecycle owner lock status inputs
- **THEN** the CLI MUST parse the flag
- **AND** the resolved preflight workflow MUST receive `require_lifecycle_owner_lock=true`.

#### Scenario: Requirement flag does not dispatch lifecycle control

- **WHEN** a caller executes `trade preflight --require-lifecycle-owner-lock`
- **THEN** the CLI MUST still dispatch `TdxTradeManager.pingan.preflight(...)`
- **AND** it MUST NOT acquire or release the lifecycle owner lock.
