## ADDED Requirements

### Requirement: Provider replay CLI SHALL expose managed daemon start/status/stop

Provider replay lifecycle control SHALL expose a minimal managed daemon control surface that can start, inspect, and stop a tool-owned replay daemon using the lifecycle statefile ownership layer.

#### Scenario: Managed daemon start records owned process metadata

- **WHEN** a caller starts a managed provider replay daemon with a config containing `lifecycle_state_file`
- **THEN** the implementation MUST launch `provider-replay serve --config <path>` as a background process
- **AND** it MUST write a lifecycle statefile with the spawned PID, owner token, generation, config hash, and `state=running`
- **AND** it MUST return the owner token and process id
- **AND** it MUST NOT start a second daemon when a valid statefile already points to a running owned PID

#### Scenario: Managed daemon status is read-only

- **WHEN** a caller requests managed daemon status
- **THEN** the implementation MUST read lifecycle statefile diagnostics
- **AND** it MUST evaluate PID liveness only when a valid PID is present
- **AND** it MUST report whether the managed daemon is running
- **AND** it MUST NOT mutate the statefile, start a process, stop a process, supervise, or schedule retries

#### Scenario: Managed daemon stop requires matching owner token

- **WHEN** a caller stops a managed provider replay daemon
- **THEN** the implementation MUST require an owner token
- **AND** it MUST validate provider id, config hash, owner token, and PID liveness before termination
- **AND** it MUST send a termination signal only to the recorded owned PID
- **AND** it MUST write a `state=stopping` lifecycle statefile after sending termination
- **AND** it MUST reject missing or mismatched owner tokens without signaling a process

#### Scenario: Managed daemon control remains bounded

- **WHEN** managed daemon start/status/stop are available
- **THEN** the implementation MUST NOT claim long-running supervision, automatic restart/backoff, port ownership inference, real provider management, broker readiness, workflow readiness, or write readiness

