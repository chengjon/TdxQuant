## ADDED Requirements

### Requirement: Subscription long-run status summary SHALL expose supervisor daemon projection

Subscription-watch status summary SHALL include an additive read-only `supervisor_daemon` projection when the background controller has a supervisor daemon status read model.

#### Scenario: Detailed status summary includes supervisor daemon projection

- **WHEN** subscription-watch background status is requested
- **AND** the controller can derive supervisor daemon status from its existing local supervisor statefile and pidfile evidence
- **THEN** `status_summary.supervisor_daemon` MUST include stable compact fields from the existing supervisor daemon status projection
- **AND** the projection MUST include `daemon_status`, `statefile_exists`, `statefile_valid`, `pidfile_exists`, `process_running`, `control_allowed`, and `boundary` when those fields are available
- **AND** the top-level detailed `supervisor_daemon` payload MUST remain present for detailed consumers

#### Scenario: Summary view preserves supervisor daemon projection

- **WHEN** bridge watch status is requested with summary view
- **THEN** the summary payload MUST include `status_summary.supervisor_daemon` when detailed status summary includes it
- **AND** the summary payload MUST NOT expose daemon command, settings, owner token, raw statefile content, or full detailed payload through this projection

#### Scenario: Supervisor daemon projection remains read-only

- **WHEN** `status_summary.supervisor_daemon` is produced
- **THEN** the projection MUST NOT start, stop, restart, supervise, backoff, probe, or mutate provider state
- **AND** the projection MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or trading readiness
