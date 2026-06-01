## ADDED Requirements

### Requirement: PingAn process lifecycle SHALL expose a controller boundary for owner and recorded-PID guard decisions

The PingAn desktop trading process lifecycle path SHALL isolate owner-lock gate evaluation, process result-shape construction, and recorded-PID guard decisions behind an explicit lifecycle controller boundary while preserving the existing public process lifecycle behavior.

#### Scenario: Controller rejects process owner gate without process side effects

- **WHEN** the lifecycle controller evaluates a process lifecycle owner gate whose owner-lock status is not owned by the requested owner token
- **THEN** it MUST return a structured owner-gate rejection decision with `owner_ok=false`
- **AND** its rejection payload MUST report `process_start_executed=false`, `process_stop_executed=false`, `process_kill_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, and `pid_ownership_claimed=false`
- **AND** the controller MUST NOT spawn, stop, kill, automate, or submit anything.

#### Scenario: Controller rejects recorded-PID guard without process side effects

- **WHEN** the lifecycle controller evaluates a stop or restart action without a usable recorded process PID, matching owner token, or matching command ownership
- **THEN** it MUST return a structured guard rejection result
- **AND** the result MUST report `process_start_executed=false`, `process_stop_executed=false`, `process_kill_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, and `pid_ownership_claimed=false`
- **AND** the controller MUST NOT call process kill, process spawn, statefile write, desktop automation, or order submission.

#### Scenario: Public process lifecycle behavior remains stable

- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_process(...)`
- **THEN** the public result shape and side-effect flags MUST remain compatible with the existing process lifecycle contract
- **AND** real process start/stop/restart execution MUST remain explicit, owner-gated, and constrained to the existing recorded-PID guarded manager path.
