## Context

The PingAn lifecycle path now has owner locks, supervisor decisions, and a recorded-PID process lifecycle command. The process lifecycle path is intentionally sensitive: `start`, `stop`, and `restart` may spawn or terminate a real desktop process when explicitly requested by an owner.

This change extracts only pure decisions from that path. The controller can decide whether the caller owns the lifecycle state and whether recorded-PID guards should reject a stop/restart request. The manager continues to own process execution, statefile I/O, and public command routing.

## Goals / Non-Goals

Goals:

- Make owner-gate and recorded-PID guard decisions testable without spawning or killing a process.
- Preserve the existing `TdxTradeManager.pingan.lifecycle_process(...)` public result shape.
- Keep `FUNCTION_TREE.md` accurate: this is architecture hardening evidence, not a production readiness promotion.

Non-goals:

- Do not move `subprocess.Popen`, `os.kill`, or statefile writes into the controller.
- Do not change PingAn buy/sell/submit-once/confirm-current trading behavior.
- Do not add a new CLI command or workflow builder capability.
- Do not claim D-07/D-08 are complete.

## Design

`PingAnLifecycleController` will gain process lifecycle helpers:

- `build_process_result(...)` builds the existing structured lifecycle process payload with side-effect flags.
- `evaluate_process_owner_gate(...)` converts owner-lock status into a side-effect-free owner decision.
- `evaluate_process_recorded_pid_guard(...)` validates recorded PID, owner token, and command ownership before stop/restart execution is allowed.
- `read_process_state(...)` normalizes the process section from a lifecycle statefile payload.

`TdxTradeManager._run_pingan_lifecycle_process(...)` will call these helpers for the pure decisions and keep the side-effecting work in the manager.

## Safety

The controller boundary must never execute process control, desktop automation, order submission, or statefile writes. Rejection payloads must keep `process_start_executed=false`, `process_stop_executed=false`, `process_kill_executed=false`, `statefile_write_executed=false`, `order_submitted=false`, and `pid_ownership_claimed=false`.

## Verification

- Red tests first for the new controller methods.
- Focused PingAn lifecycle tests.
- Full `tests/test_trade_manager.py`.
- `openspec validate --all --strict`.
- `git diff --check`.
- `python scripts/validate_function_tree_registry.py`.
