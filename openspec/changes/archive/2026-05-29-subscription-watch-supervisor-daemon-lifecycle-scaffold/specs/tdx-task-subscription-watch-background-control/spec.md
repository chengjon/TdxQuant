## ADDED Requirements

### Requirement: Subscription watch background control SHALL provide an explicit supervisor daemon lifecycle scaffold

The worker-local subscription-watch background controller SHALL provide a local, explicit, opt-in lifecycle scaffold for an owned supervisor daemon process.

#### Scenario: Supervisor daemon start writes owned state

- **WHEN** a caller explicitly starts the supervisor daemon with bounded supervisor run settings
- **THEN** the controller MUST launch a daemon command and persist a supervisor daemon statefile with schema version, state, pid, owner token, generation, command, supervisor settings, and boundary
- **AND** it MUST write a separate supervisor pidfile
- **AND** it MUST NOT overwrite the subscription-watch active run statefile or pidfile.

#### Scenario: Supervisor daemon status is read-only

- **WHEN** a caller checks supervisor daemon status
- **THEN** the controller MUST derive missing/running/not-running/invalid status from the supervisor statefile, pidfile, and pid liveness
- **AND** it MUST NOT call `supervisor_tick()`, `supervisor_run()`, `start()`, `stop()`, or `restart()`.

#### Scenario: Supervisor daemon stop requires ownership

- **WHEN** a caller stops the supervisor daemon
- **THEN** the controller MUST require the supplied owner token to match the supervisor statefile owner token before signaling the recorded pid
- **AND** it MUST write a stopping supervisor state only after a signal is sent
- **AND** it MUST NOT signal any pid when the statefile is missing, invalid, not running, or owned by a different token.

#### Scenario: Supervisor daemon runner loops over bounded supervisor run

- **WHEN** the supervisor daemon command is executed
- **THEN** it MUST repeatedly call the existing bounded `supervisor_run()` operation using explicit max-ticks, interval, loop-sleep, and reason settings
- **AND** it MUST NOT introduce HTTP, CLI, bridge registry, catalog, task, report, trade, or workflow entrypoints in this slice.
