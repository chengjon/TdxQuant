## ADDED Requirements

### Requirement: Subscription long-run status summary SHALL expose statefile ownership projection

Subscription-watch status summary SHALL include an additive read-only `statefile_ownership` projection when the background controller has local statefile ownership diagnostics.

#### Scenario: Detailed status summary includes statefile ownership projection

- **WHEN** subscription-watch background status is requested
- **AND** the controller derives local statefile ownership diagnostics from existing statefile and pidfile evidence
- **THEN** `status_summary.statefile_ownership` MUST include compact stable fields from the existing `statefile_ownership` diagnostic
- **AND** the projection MUST include `status`, `reason_codes`, `statefile_exists`, `pidfile_exists`, `active`, `control_state`, `pid_matches_owned_state`, and `boundary` when those fields are available
- **AND** the top-level detailed `statefile_ownership` payload MUST remain present for detailed consumers

#### Scenario: Summary view preserves statefile ownership projection

- **WHEN** bridge watch status is requested with summary view
- **THEN** the summary payload MUST include `status_summary.statefile_ownership` when detailed status summary includes it
- **AND** the summary payload MUST NOT expose raw statefile content, lock handles, command arguments, or full detailed payload through this projection

#### Scenario: Statefile ownership projection remains read-only

- **WHEN** `status_summary.statefile_ownership` is produced
- **THEN** the projection MUST NOT acquire the control lock, start, stop, restart, supervise, backoff, probe, or mutate provider state
- **AND** the projection MUST NOT claim provider readiness, broker readiness, live行情 availability, production lifecycle health, or process ownership beyond local PID evidence
