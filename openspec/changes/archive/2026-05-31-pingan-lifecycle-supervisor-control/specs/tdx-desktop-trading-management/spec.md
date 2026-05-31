## ADDED Requirements

### Requirement: Desktop trading management SHALL expose PingAn lifecycle supervisor control

Desktop trading management SHALL expose explicit PingAn lifecycle supervisor tick and bounded foreground run operations that are guarded by the existing local lifecycle owner lock before recording restart/backoff decisions.

#### Scenario: Supervisor tick rejects unowned lifecycle state without control side effects

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick` without an owned local lifecycle statefile for the provided owner token
- **THEN** the result MUST report `supervisor_owned=false`
- **AND** the result MUST report `control_dispatch_executed=false`
- **AND** the result MUST report `restart_executed=false`
- **AND** the result MUST report `backoff_executed=false`
- **AND** the result MUST NOT call broker health observation.

#### Scenario: Supervisor tick records restart and backoff decisions under ownership

- **GIVEN** a caller has acquired the local PingAn lifecycle owner lock for the provided owner token
- **WHEN** `TdxTradeManager.pingan.lifecycle_supervisor_tick` observes unhealthy broker health
- **THEN** the first eligible tick MUST write a local lifecycle statefile supervisor update with `restart_executed=true`
- **AND** a later tick inside the configured backoff window MUST write a local lifecycle statefile supervisor update with `backoff_executed=true`
- **AND** both updates MUST report `order_submitted=false`, `process_kill_executed=false`, and `pid_ownership_claimed=false`.

#### Scenario: Supervisor run bounds the number of control ticks

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_run` with `max_ticks=N`
- **THEN** the operation MUST execute no more than `N` supervisor ticks
- **AND** the returned summary MUST include the observed tick count and per-tick results.
