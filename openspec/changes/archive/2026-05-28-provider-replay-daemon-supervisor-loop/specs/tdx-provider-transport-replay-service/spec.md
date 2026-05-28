## ADDED Requirements

### Requirement: Provider replay CLI SHALL expose a foreground managed daemon supervisor

Provider replay lifecycle control SHALL expose a foreground supervisor that owns one managed replay daemon process, refreshes lifecycle heartbeat state, and records child exit state without automatic restart/backoff.

#### Scenario: Supervisor writes heartbeat state while child is running

- **WHEN** a caller runs the managed daemon supervisor
- **THEN** the supervisor MUST launch `provider-replay serve --config <path>`
- **AND** it MUST write a lifecycle statefile with `state=supervising`
- **AND** it MUST refresh the statefile heartbeat while the child remains running
- **AND** it MUST return the owner token, child PID, heartbeat count, and command metadata

#### Scenario: Supervisor records child exit without restart

- **WHEN** the supervised child exits
- **THEN** the supervisor MUST write a lifecycle statefile with `state=exited`
- **AND** it MUST report the child exit code
- **AND** it MUST NOT relaunch the child
- **AND** it MUST NOT schedule restart/backoff

#### Scenario: Supervisor interruption records stopping state

- **WHEN** the supervisor is interrupted while the child is running
- **THEN** it MUST attempt to terminate the child
- **AND** it MUST write a lifecycle statefile with `state=stopping`
- **AND** it MUST return an interrupted supervisor status

#### Scenario: Supervisor control remains bounded

- **WHEN** the foreground supervisor is available
- **THEN** the implementation MUST NOT claim automatic restart/backoff, recovery policy, port ownership inference, real provider management, broker readiness, workflow readiness, or write readiness

