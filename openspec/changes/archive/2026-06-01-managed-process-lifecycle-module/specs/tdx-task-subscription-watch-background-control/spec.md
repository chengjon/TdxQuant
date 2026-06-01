# tdx-task-subscription-watch-background-control Specification

## ADDED Requirements

### Requirement: Subscription watch background ownership SHALL use shared managed lifecycle provenance

Subscription watch background statefile ownership diagnostics SHALL expose provenance showing that PID parsing, liveness, and ownership projection are backed by the shared managed-process lifecycle module.

#### Scenario: Background statefile ownership includes managed lifecycle provenance

- **WHEN** a caller builds subscription watch background statefile ownership
- **THEN** the returned ownership payload MUST include `managed_lifecycle`
- **AND** `managed_lifecycle.adapter` MUST be `subscription_watch_background`
- **AND** `managed_lifecycle.primitives` MUST include `pid_coercion`, `process_liveness`, and `statefile_ownership`
- **AND** the ownership payload MUST remain read-only and MUST NOT start, stop, restart, supervise, or signal a watch process.
