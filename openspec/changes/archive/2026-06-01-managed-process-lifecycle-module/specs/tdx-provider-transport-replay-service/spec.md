# tdx-provider-transport-replay-service Specification

## ADDED Requirements

### Requirement: Provider replay lifecycle diagnostics SHALL use shared managed lifecycle provenance

Provider replay managed-daemon status and ownership diagnostics SHALL expose provenance showing that process liveness and ownership diagnostics are backed by the shared managed-process lifecycle module.

#### Scenario: Provider replay status includes managed lifecycle provenance

- **WHEN** a caller builds provider replay managed daemon status
- **THEN** the returned ownership diagnostics MUST include `managed_lifecycle`
- **AND** `managed_lifecycle.adapter` MUST be `provider_transport_replay`
- **AND** `managed_lifecycle.primitives` MUST include `process_liveness` and `process_ownership`
- **AND** the status MUST remain read-only and MUST NOT open a socket, start a server, stop a server, or supervise a process.
