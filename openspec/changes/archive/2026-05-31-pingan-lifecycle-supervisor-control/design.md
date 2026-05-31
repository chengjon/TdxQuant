# Design: PingAn lifecycle supervisor control

## Scope

The control surface is deliberately narrow:

- `TdxTradeManager.pingan.lifecycle_supervisor_tick(...)` performs one bounded control decision.
- `TdxTradeManager.pingan.lifecycle_supervisor_run(...)` repeats the tick a caller-specified number of times.
- CLI wrappers expose the same behavior as explicit operator commands.

The supervisor is local and statefile-backed. It does not own the real PingAn desktop process identity and does not kill/start the PingAn process. It records restart/backoff decisions as local lifecycle evidence, guarded by the existing lifecycle owner lock.

## Ownership Gate

Every control tick first calls the existing lifecycle owner-lock status path using `statefile_path`, `owner_token`, and `stale_after_seconds`.

The tick is rejected as a no-op when:

- the statefile/lock is missing,
- the current owner token differs,
- the state is stale,
- PID validation reports that the owner PID is no longer alive.

Rejected ticks return structured evidence with `control_dispatch_executed=false`, `restart_executed=false`, `backoff_executed=false`, and `statefile_write_executed=false`.

## Health Observation

When ownership is valid, the tick calls `PingAnBrokerAdapter.health_check()` through the manager's configured `title_keyword` and `exe_path`. A healthy result records an observation and resets failure/backoff state in the local lifecycle statefile.

## Restart And Backoff Recording

When health is not OK, the tick reads prior supervisor state from the lifecycle statefile:

- If the last restart attempt is inside the configured `backoff_seconds` window, the tick records `backoff_executed=true` and does not record a new restart attempt.
- If the attempt count has reached `max_restart_attempts`, the tick records `status=max_restart_attempts_reached` and does not record another restart attempt.
- Otherwise, the tick records a controlled restart attempt with `restart_executed=true` and increments the attempt counter.

This is local lifecycle control evidence. It is not OS process restart. The payload explicitly keeps `process_kill_executed=false`, `pid_ownership_claimed=false`, and `order_submitted=false`.

## Foreground Run

`lifecycle_supervisor_run(max_ticks, interval_seconds, ...)` executes at most `max_ticks` ticks and sleeps between ticks only when `interval_seconds > 0` and another tick remains. Tests use `interval_seconds=0`.

## FUNCTION_TREE Registration

D-07 and D-08 remain `[部分实现]`. Their evidence gains the manager methods, CLI entrypoints, focused tests, and this OpenSpec change. Their boundaries must state this is local statefile-backed lifecycle control only, not live/manual acceptance, workflow execution, or production trading readiness.
