# tdx-desktop-trading-preflight Specification

## Purpose
TBD - created by archiving change add-trade-preflight-readiness. Update Purpose after archive.
## Requirements
### Requirement: Stable desktop trading SHALL expose a read-only request preflight workflow
The system SHALL expose a stable non-side-effecting preflight workflow for one concrete Ping An desktop trade request.

#### Scenario: Caller runs stable Ping An trade preflight
- **WHEN** a caller executes `TdxTradeManager.pingan.preflight(...)` with the requested trade inputs
- **THEN** the result MUST include a structured preflight summary for that concrete trade request
- **AND** the summary MUST include named checks for broker/runtime readiness, buy-page detection, order-request risk gate, and HID path status

### Requirement: Stable desktop trading preflight SHALL evaluate submission-key readiness without side effects
The system SHALL evaluate stable submission-key idempotency semantics during preflight without performing any desktop execution.

#### Scenario: Caller provides submission key during preflight
- **WHEN** a caller executes the stable trade preflight workflow with a `submission_key`
- **THEN** the preflight summary MUST include the idempotency outcome for that key and normalized request

#### Scenario: Preflight detects conflicting submission key
- **WHEN** a caller executes the stable trade preflight workflow with a `submission_key` that conflicts with a previously recorded side-effecting request
- **THEN** the preflight workflow MUST return a failed-style result
- **AND** the preflight summary MUST mark the idempotency check as failed

### Requirement: Stable desktop trading preflight SHALL remain non-side-effecting
The system SHALL keep the stable trade preflight workflow read-only.

#### Scenario: Trade preflight does not write execution artifacts
- **WHEN** a caller executes the stable trade preflight workflow
- **THEN** the workflow MUST NOT write last-order state
- **AND** it MUST NOT append an order event row
- **AND** it MUST NOT append a submission-ledger row

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

