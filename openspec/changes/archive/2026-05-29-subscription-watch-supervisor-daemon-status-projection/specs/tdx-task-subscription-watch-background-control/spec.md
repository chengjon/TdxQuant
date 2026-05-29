## ADDED Requirements

### Requirement: Subscription watch background status SHALL include read-only supervisor daemon status

The worker-local background status read model SHALL include the supervisor daemon status without executing supervisor daemon lifecycle control.

#### Scenario: Status includes supervisor daemon read model

- **WHEN** a caller requests background watch status
- **THEN** the response MUST include a `supervisor_daemon` object derived from the existing supervisor daemon status operation
- **AND** it MUST include daemon status, statefile validity, pidfile presence, PID, process-running flag, owner-token presence or owner identity metadata, generation, and control allowance when available
- **AND** it MUST NOT call supervisor daemon start, stop, supervisor tick, supervisor run, restart, task, report, trade, workflow, or catalog execution.

#### Scenario: Missing supervisor daemon files remain read-only status

- **WHEN** supervisor daemon state files are missing or invalid
- **THEN** background watch status MUST report the missing or invalid daemon status as data
- **AND** it MUST NOT create, repair, delete, lock, start, stop, or rewrite supervisor daemon files.
