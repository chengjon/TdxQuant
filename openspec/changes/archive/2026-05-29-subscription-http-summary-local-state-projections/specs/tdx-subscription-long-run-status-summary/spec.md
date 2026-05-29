## ADDED Requirements

### Requirement: Subscription HTTP summary view SHALL preserve local state projections

HTTP `GET /bridge/v1/watch/status?view=summary` SHALL preserve compact local-state projections already present in detailed `status_summary`.

#### Scenario: HTTP summary view includes statefile ownership projection

- **WHEN** HTTP watch status summary view is requested
- **AND** detailed status includes `status_summary.statefile_ownership`
- **THEN** the HTTP summary payload MUST include `status_summary.statefile_ownership`
- **AND** it MUST NOT expose raw statefile content, lock handles, command arguments, or full detailed payload through this projection

#### Scenario: HTTP summary view includes supervisor daemon projection

- **WHEN** HTTP watch status summary view is requested
- **AND** detailed status includes `status_summary.supervisor_daemon`
- **THEN** the HTTP summary payload MUST include `status_summary.supervisor_daemon`
- **AND** the existing top-level summary `supervisor_daemon` projection MAY remain present for compatibility
- **AND** the projection MUST NOT expose owner token, command, settings, raw statefile content, or full detailed payload

#### Scenario: HTTP local-state projections remain read-only

- **WHEN** HTTP summary view preserves local-state projections
- **THEN** it MUST NOT start, stop, restart, supervise, backoff, probe, mutate provider state, or stream events
- **AND** it MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or trading readiness
