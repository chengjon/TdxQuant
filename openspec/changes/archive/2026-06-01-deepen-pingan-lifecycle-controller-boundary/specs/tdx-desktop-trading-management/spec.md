## ADDED Requirements

### Requirement: PingAn lifecycle supervisor SHALL expose a controller boundary for safety gate and restart policy decisions
The PingAn desktop trading lifecycle supervisor SHALL isolate owner-lock gate evaluation and restart/backoff policy decisions behind an explicit lifecycle controller boundary while preserving the existing trade manager public lifecycle methods.

#### Scenario: Controller rejects supervisor tick without owner side effects
- **WHEN** the lifecycle controller evaluates a supervisor tick whose owner-lock status is not owned by the requested owner token
- **THEN** it MUST return a structured owner-gate rejection payload with `supervisor_owned=false`
- **AND** it MUST report `control_dispatch_executed=false`, `restart_executed=false`, `backoff_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, `process_kill_executed=false`, and `pid_ownership_claimed=false`

#### Scenario: Controller decides restart and backoff without executing process control
- **WHEN** the lifecycle controller evaluates unhealthy broker state under an owned supervisor state
- **THEN** it MUST identify the first eligible restart decision and subsequent backoff decision from prior supervisor state
- **AND** the controller decision MUST NOT execute process start, stop, kill, order submission, or desktop automation

#### Scenario: Public supervisor tick preserves existing lifecycle behavior
- **WHEN** a caller invokes `TdxTradeManager.pingan.lifecycle_supervisor_tick`
- **THEN** the public result shape and safety fields MUST remain compatible with the existing lifecycle supervisor contract
- **AND** actual process restart MUST remain opt-in and delegated to the existing recorded-PID guarded lifecycle process path
