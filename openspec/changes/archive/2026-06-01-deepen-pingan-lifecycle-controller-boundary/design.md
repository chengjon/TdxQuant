## Context

The PingAn lifecycle path already supports local owner locks, bounded supervisor ticks/runs, restart/backoff records, statefile writes, and opt-in recorded-PID process restart. The current supervisor tick implementation is broad enough that unrelated future changes can accidentally affect the safety gate or restart policy.

This change creates a controller boundary for pure lifecycle supervisor decisions. The public trade manager API remains stable, and side-effecting work stays on the existing guarded paths.

## Goals / Non-Goals

**Goals:**

- Isolate owner-gate rejection decisions and restart/backoff policy decisions behind a named PingAn lifecycle controller boundary.
- Preserve existing `TdxTradeManager.pingan.lifecycle_supervisor_tick` result fields.
- Keep statefile writes, broker health checks, and optional process restart behavior unchanged.
- Add tests that exercise the new decision boundary and the existing public trade manager path.

**Non-Goals:**

- No rewrite of process start/stop/restart execution.
- No UIA/HID or desktop click behavior changes.
- No multi-broker lifecycle platform.
- No order retry, order submission, catalog execution, task execution, or workflow builder semantics.
- No lifecycle daemon loop redesign in this slice.

## Decisions

1. Start with pure decisions instead of moving the full supervisor tick implementation.

   Rationale: the supervisor tick function performs guarded side effects. Extracting pure decisions first lowers risk and gives later lifecycle work a stable place to grow.

   Alternative considered: move the entire `_run_pingan_lifecycle_supervisor_tick` function into a new module immediately. Rejected because it would require moving or injecting many statefile, process, timestamp, and broker dependencies in one change.

2. Keep the existing public manager method as the compatibility facade.

   Rationale: CLI, tasks, tests, and callers already use `TdxTradeManager.pingan.lifecycle_supervisor_tick`. The architecture issue is implementation locality, not the public method.

3. Treat controller output as local lifecycle evidence only.

   Rationale: restart/backoff decisions and immediate health rechecks do not prove order readiness, UI login readiness, or production broker readiness.

## Risks / Trade-offs

- The first boundary will be a tracer, not a full lifecycle rewrite → mark the boundary clearly in `FUNCTION_TREE.md`.
- Controller tests could become implementation-coupled if they assert private function placement → test the controller as a public module-level boundary and keep existing manager behavior tests.
- Side-effecting process restart still lives in `manager.py` → acceptable for this slice because the goal is decision boundary extraction, not process execution migration.

## Migration Plan

1. Add red tests for the lifecycle controller owner gate and restart/backoff decision behavior.
2. Add the controller module and route supervisor tick through it for those decisions.
3. Run focused lifecycle tests.
4. Update `FUNCTION_TREE.md`, validate OpenSpec, archive, and repeat verification.
