# tdx-managed-process-lifecycle Specification

## ADDED Requirements

### Requirement: Managed process lifecycle SHALL expose shared liveness primitives

The system SHALL provide shared lifecycle primitives for coercing process IDs and reporting process liveness without starting, stopping, or signaling managed runtimes beyond the configured liveness probe.

#### Scenario: Caller builds liveness for an invalid PID

- **WHEN** a caller builds managed-process liveness for a missing, non-numeric, zero, or negative PID
- **THEN** the result MUST identify the PID as invalid
- **AND** it MUST report `pid_live=false`
- **AND** it MUST include a stable schema identifier.

#### Scenario: Caller builds liveness for a valid PID

- **WHEN** a caller builds managed-process liveness for a positive PID with an injected liveness probe
- **THEN** the result MUST include the normalized integer PID
- **AND** it MUST report the boolean liveness value returned by the probe
- **AND** it MUST NOT mutate any lifecycle statefile, lock, or process.

### Requirement: Managed process lifecycle SHALL expose ownership diagnostics

The system SHALL provide shared diagnostics for process ownership checks so adapters can consistently report PID validity, PID liveness, owner token presence, owner token match, process identity check status, and control eligibility.

#### Scenario: Ownership diagnostics reject invalid state

- **WHEN** ownership diagnostics are built without a configured or valid statefile check
- **THEN** the result MUST report a non-owned status
- **AND** it MUST set `control_allowed=false`
- **AND** it MUST include a boundary stating that the result is read-only diagnostics.

#### Scenario: Ownership diagnostics accept a matching live process

- **WHEN** ownership diagnostics receive a valid statefile check with a live PID, matching owner token, and matching process identity
- **THEN** the result MUST report `ownership_status=owned`
- **AND** it MUST set `owned_process=true`
- **AND** it MUST set `control_allowed=true`.

### Requirement: Managed process lifecycle SHALL expose adapter provenance

The system SHALL provide a stable provenance object that adapters can include in lifecycle status outputs.

#### Scenario: Adapter includes managed lifecycle provenance

- **WHEN** an adapter uses shared managed-process lifecycle primitives
- **THEN** its status output MUST include `managed_lifecycle`
- **AND** `managed_lifecycle.module` MUST be `tdxquant.managed_lifecycle`
- **AND** `managed_lifecycle.adapter` MUST identify the adapter
- **AND** `managed_lifecycle.primitives` MUST list the shared primitive names used by the adapter.

### Requirement: Managed process lifecycle SHALL expose restart backoff projection

The system SHALL provide a shared helper for projecting bounded restart backoff metadata without scheduling or executing a restart.

#### Scenario: Caller builds restart backoff projection

- **WHEN** a caller builds a restart backoff projection from a reason, timestamp, and backoff duration
- **THEN** the result MUST include `status=active`, `reason`, `created_at`, `retry_after_at`, and `backoff_seconds`
- **AND** the helper MUST NOT sleep, restart, stop, or start any process.
