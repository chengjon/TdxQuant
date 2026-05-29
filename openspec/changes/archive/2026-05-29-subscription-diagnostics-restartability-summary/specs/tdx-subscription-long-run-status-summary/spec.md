## ADDED Requirements

### Requirement: Subscription watch-status diagnostics SHALL expose restartability summary

Subscription watch-status diagnostics SHALL include an additive read-only restartability summary derived from existing detailed status data without triggering lifecycle control.

#### Scenario: Diagnostics projects restartable active state

- **WHEN** diagnostics view is built from detailed status whose `control` payload is active and includes a valid persisted `start_request`
- **THEN** `diagnostics.restartability.ready` MUST be `true`
- **AND** `diagnostics.restartability.decision` MUST be `ready`
- **AND** `diagnostics.restartability.reason_codes` MUST be empty
- **AND** `diagnostics.restartability.start_request_summary` MUST include compact request shape fields
- **AND** diagnostics MUST NOT expose raw `control`, raw `watch_status`, full governance reasons, or full governance actions.

#### Scenario: Diagnostics projects blocked restartability reasons

- **WHEN** diagnostics view is built from detailed status that is not restartable
- **THEN** `diagnostics.restartability.ready` MUST be `false`
- **AND** `diagnostics.restartability.decision` MUST be `blocked`
- **AND** `diagnostics.restartability.reason_codes` MUST include stable reason code `NO_ACTIVE_RUN`, `MISSING_START_REQUEST`, or `INVALID_START_REQUEST`
- **AND** diagnostics MUST NOT stop, start, restart, signal, schedule backoff, or run a supervisor loop.
