## ADDED Requirements

### Requirement: PingAn lifecycle supervisor SHALL optionally execute recorded-PID process restart

PingAn lifecycle supervisor tick/run SHALL optionally execute the existing recorded-PID guarded process restart when the supervisor restart/backoff policy allows a restart and the caller explicitly opts in.

#### Scenario: Eligible supervisor restart executes recorded-PID process restart when opted in

- **GIVEN** the lifecycle owner lock is owned by the caller
- **AND** the lifecycle statefile contains a process PID recorded by the same owner token and command
- **AND** broker health is unhealthy
- **AND** restart/backoff policy allows a restart attempt
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick(process_restart_enabled=true)`
- **THEN** the supervisor MUST call the existing `lifecycle_process(action=restart)` path
- **AND** the supervisor payload MUST report `process_restart_requested=true`
- **AND** the supervisor payload MUST report `process_restart_executed=true` when the recorded-PID restart succeeds
- **AND** the supervisor payload MUST include the process restart result summary.

#### Scenario: Backoff prevents process restart even when opt-in is enabled

- **GIVEN** a prior supervisor restart attempt is still inside the configured backoff window
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick(process_restart_enabled=true)`
- **THEN** the supervisor MUST report `backoff_executed=true`
- **AND** the supervisor MUST report `process_restart_requested=false`
- **AND** the supervisor MUST NOT call process lifecycle restart.

#### Scenario: Default supervisor restart remains statefile-only

- **WHEN** a supervisor restart is eligible but `process_restart_enabled=false`
- **THEN** the supervisor MUST preserve the existing statefile-backed restart decision behavior
- **AND** it MUST report `process_restart_requested=false`
- **AND** it MUST NOT call process lifecycle restart.
