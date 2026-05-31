## ADDED Requirements

### Requirement: Desktop trading management SHALL expose explicit PingAn process lifecycle control

Desktop trading management SHALL expose explicit local PingAn process lifecycle status/start/stop/restart operations that are guarded by the existing lifecycle owner lock and constrained to the process PID recorded in the lifecycle statefile.

#### Scenario: Mutating process lifecycle actions reject missing owner lock

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_process(action=start|stop|restart)` without a matching owned lifecycle owner lock
- **THEN** the result MUST be rejected
- **AND** the result MUST report `process_start_executed=false`
- **AND** the result MUST report `process_stop_executed=false`
- **AND** the result MUST report `process_kill_executed=false`
- **AND** the result MUST NOT spawn or terminate a process.

#### Scenario: Start records an owned process PID

- **GIVEN** a caller has acquired the local PingAn lifecycle owner lock
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=start, exe_path=<path>)`
- **THEN** the manager MUST start the executable through a bounded subprocess call
- **AND** the manager MUST write the spawned PID, command, owner token, and start timestamp to the lifecycle statefile
- **AND** the result MUST report `pid_ownership_claimed=true` for that spawned process.

#### Scenario: Stop only targets the recorded owned PID

- **GIVEN** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=stop)`
- **THEN** the manager MUST terminate only the recorded PID
- **AND** the manager MUST write stop evidence to the lifecycle statefile
- **AND** the result MUST NOT claim broad PingAn process discovery or unrelated PID ownership.

#### Scenario: Restart is composed from guarded recorded PID stop and start

- **GIVEN** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **WHEN** the caller invokes `TdxTradeManager.pingan.lifecycle_process(action=restart)`
- **THEN** the manager MUST record a restart operation using the same recorded-PID guard as stop
- **AND** the manager MUST write the newly spawned PID to the lifecycle statefile.
