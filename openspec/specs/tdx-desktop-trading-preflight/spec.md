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

### Requirement: PingAn preflight SHALL identify readiness evidence provenance

`TdxTradeManager.pingan.preflight(...)` SHALL include artifact provenance metadata for the promotion gate status evidence it returns.

#### Scenario: Preflight output carries provenance accepted by promotion readiness rollup

- **WHEN** `TdxTradeManager.pingan.preflight(...)` returns a `promotion_gate_status`
- **THEN** result data SHALL include `artifact_provenance`
- **AND** `artifact_provenance.schema` SHALL be `tdx.desktop_trade.pingan_readiness_evidence_artifact.v1`
- **AND** `artifact_provenance.source_kind` SHALL be `preflight`
- **AND** `artifact_provenance.producer` SHALL be `trade preflight`
- **AND** `artifact_provenance.evidence_schema` SHALL match `tdx.desktop_trade.pingan_promotion_gate_status.v1`
- **AND** the preflight workflow SHALL remain read-only and SHALL NOT submit orders.

