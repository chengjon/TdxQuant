# Design: PingAn process lifecycle control

## Interface

`TdxTradeManager.pingan.lifecycle_process(...)` accepts:

- `action`: `status`, `start`, `stop`, or `restart`
- `statefile_path`
- `owner_token`
- `exe_path`
- `stale_after_seconds`
- optional `force_restart`

The CLI exposes the same fields through `trade lifecycle-process`.

## Ownership Model

The controller reuses the existing lifecycle owner lock. Mutating actions (`start`, `stop`, `restart`) are rejected unless:

- the lifecycle owner lock is `owned`,
- the current owner token matches,
- the owner lock is not stale,
- the owner PID is alive.

Status is read-only but still reports owner-lock status and process ownership diagnostics.

## Process Identity

The controller records only processes it starts:

- `process_pid`
- `process_command`
- `process_owner_token`
- `process_started_at`
- `process_status`

Stop/restart only target the recorded PID when the owner token matches and the recorded command matches the requested `exe_path`. This avoids broad process discovery and prevents killing unrelated desktop processes.

## Side Effects

`start` calls `subprocess.Popen([exe_path], start_new_session=True)` and writes the lifecycle statefile.

`stop` calls `os.kill(recorded_pid, signal.SIGTERM)` only for the recorded PID and writes the lifecycle statefile.

`restart` combines a guarded stop of the recorded PID with a guarded start of the configured executable. If a recorded PID is already not running, it records that condition and still starts a new owned process.

## Boundaries

This slice gives explicit process lifecycle evidence. It does not prove UI login state, broker readiness, successful market/trade connectivity, or live/manual acceptance. D-07 and D-08 therefore remain `[部分实现]`.
