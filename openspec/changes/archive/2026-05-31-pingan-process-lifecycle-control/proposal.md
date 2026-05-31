# Change: PingAn process lifecycle control

## Why

D-07 and D-08 now have local lifecycle owner locks plus a statefile-backed supervisor tick/run loop. That loop still explicitly says it does not own, start, stop, kill, or restart the real PingAn desktop process. The next implementation step is an explicit operator-owned process lifecycle controller that can start a configured PingAn executable, report the spawned PID state, stop only that recorded PID, and restart it under the same owner lock.

This closes a concrete portion of the desktop lifecycle gap without changing trading behavior.

## What Changes

- Add `TdxTradeManager.pingan.lifecycle_process(action=...)` for `status`, `start`, `stop`, and `restart`.
- Require the existing local lifecycle owner lock before any start/stop/restart side effect.
- Start PingAn through a caller-provided `exe_path` and persist spawned PID, command, owner token, and lifecycle timestamps into the lifecycle statefile.
- Stop/restart only the PID recorded in the lifecycle statefile for the same owner token.
- Add `trade lifecycle-process` CLI entrypoint.
- Register the evidence in `FUNCTION_TREE.md` D-07/D-08 while keeping both nodes `[部分实现]`.

## Non-Goals

- No order submission, confirmation click, retry/resubmit, or workflow execution.
- No broad process discovery or killing unrelated PingAn/TongDaXin processes.
- No production readiness claim, broker readiness claim, or live/manual acceptance claim.
- No automatic long-running OS service installation.
