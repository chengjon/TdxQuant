## ADDED Requirements

### Requirement: Provider replay lifecycle SHALL write ownership statefiles under lock

Provider replay lifecycle support SHALL provide an internal statefile writer that records daemon ownership metadata under an exclusive lock and atomically replaces the configured lifecycle statefile.

#### Scenario: Ownership statefile write records canonical metadata

- **WHEN** a caller writes a provider replay lifecycle statefile for a config with `lifecycle_state_file`
- **THEN** the write result MUST report `write_status` as `written`
- **AND** the writer MUST acquire and release a lock file associated with the statefile
- **AND** the persisted JSON MUST include the lifecycle schema version, provider id, integer pid, state, owner token, generation, config hash, and updated timestamp
- **AND** the persisted JSON MUST NOT include the raw provider token
- **AND** the write MUST be atomic from the caller contract perspective

#### Scenario: Existing lock blocks statefile mutation

- **WHEN** the associated lock file already exists
- **THEN** the write result MUST report `write_status` as `locked`
- **AND** the writer MUST NOT replace the existing statefile
- **AND** the result MUST include a lock error
- **AND** the command MUST NOT start, stop, restart, supervise, probe runtime, or inspect processes

#### Scenario: Read-only statefile diagnostics report ownership fields when present

- **WHEN** a caller checks a statefile written by the lifecycle statefile writer
- **THEN** diagnostics MUST report the owner token, generation, config hash, and config hash match status
- **AND** the check result MUST remain read-only
- **AND** the check result MUST NOT treat a valid statefile as daemon readiness, process ownership proof, supervisor health, write capability, or lifecycle control permission

#### Scenario: Statefile ownership layer is not daemon lifecycle control

- **WHEN** lifecycle statefile ownership helpers are available
- **THEN** provider replay lifecycle status and readiness MUST still avoid claiming daemon start/stop/restart, long-running supervision, restart/backoff scheduling, process liveness, port ownership, real provider management, broker readiness, workflow readiness, or write readiness

