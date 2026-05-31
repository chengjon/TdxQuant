## ADDED Requirements

### Requirement: Trade preflight CLI SHALL accept lifecycle owner lock status inputs

The stable `trade preflight` CLI SHALL accept optional inputs for a read-only PingAn lifecycle owner lock status check.

#### Scenario: Caller provides lifecycle owner lock status inputs to trade preflight

- **WHEN** a caller executes `trade preflight` with `--lifecycle-statefile-path`, `--lifecycle-owner-token`, and `--lifecycle-stale-after-seconds`
- **THEN** the CLI MUST parse those arguments
- **AND** the resolved preflight workflow MUST receive those values unchanged.

#### Scenario: Trade preflight CLI owner lock inputs remain read-only

- **WHEN** a caller executes `trade preflight` with lifecycle owner lock status inputs
- **THEN** the CLI MUST dispatch `TdxTradeManager.pingan.preflight(...)`
- **AND** it MUST NOT dispatch `TdxTradeManager.pingan.lifecycle_owner_lock(...)` with `action=acquire` or `action=release`.
