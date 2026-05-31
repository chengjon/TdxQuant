# Design: PingAn supervisor process restart control

## Scope

The integration adds a narrow bridge from supervisor restart policy to process lifecycle restart:

- `process_restart_enabled=False` by default.
- `process_restart_exe_path` may override the manager `exe_path` for the process restart command.
- `force_process_restart` is forwarded to `lifecycle_process(action=restart)`.

## Control Flow

During a supervisor tick:

1. Verify lifecycle owner lock as already implemented.
2. Observe broker health.
3. If broker health is healthy, reset supervisor failure state and do not execute process restart.
4. If broker health is unhealthy and the tick is inside backoff, record backoff and do not execute process restart.
5. If broker health is unhealthy and max restart attempts are exhausted, do not execute process restart.
6. If broker health is unhealthy and restart is eligible:
   - record the supervisor restart attempt,
   - when `process_restart_enabled=True`, call `lifecycle_process(action=restart)` with the same `statefile_path`, `owner_token`, stale timeout, and selected executable path,
   - surface the lifecycle process result in the supervisor payload.

## Statefile Ordering

The supervisor writes restart/backoff state first. The process restart then updates the same lifecycle statefile through the existing process lifecycle writer. The supervisor result payload includes the process restart result, but the process writer remains the authority for recorded PID state.

## Boundaries

This is still explicit operator-owned lifecycle control. It does not execute trading workflows. It does not kill arbitrary PingAn processes. It only delegates to `lifecycle_process(restart)`, whose recorded PID, owner-token, and command guards remain authoritative.
