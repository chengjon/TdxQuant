## Context

`last_restart_observation` already protects against stale writes by checking that the active statefile still points at the replacement run before merging the observation. `last_supervisor_tick_observation` and `last_supervisor_run_observation` currently merge into any existing active payload. That is best-effort and usually fine, but it can mislead diagnostics if another control action moves the statefile to a different run before the observation write.

This change aligns supervisor observation writes with the restart observation boundary: write the compact observation only when the current statefile still belongs to the run associated with the tick/run result. When no expected run id is available, existing best-effort behavior is preserved.

## Goals / Non-Goals

Goals:

- Guard supervisor tick observation persistence when a tick has an expected current run id.
- Guard supervisor run observation persistence when the aggregate result carries a recovered or previous run id.
- Keep returned tick/run payloads unchanged.
- Keep diagnostics schema unchanged; diagnostics simply reflect whether an observation was safely persisted.

Non-goals:

- No new HTTP, CLI, registry, catalog, task, report, trade, or workflow entrypoint.
- No background supervisor daemon, timer, scheduler, automatic retry, or lock-owner service.
- No provider readiness, broker readiness, or live availability assertion.
- No history ledger or raw payload exposure.

## Decisions

- Use an optional expected-run guard instead of introducing a new statefile schema. This keeps the change local to observation persistence and avoids widening the diagnostics contract.
- If `expected_run_id` is known and the active payload `run_id` differs, skip the observation write. The control operation result remains authoritative for the caller that invoked it.
- If no active payload exists, keep existing no-op persistence behavior.
- If no expected run id is known, keep existing best-effort persistence so wait/noop observations with no ownership evidence are not silently lost.

## Risks / Trade-offs

- A skipped observation means diagnostics may not show the most recent manual tick/run if ownership changed concurrently. That is preferable to attaching stale observation data to the wrong run.
- The guard is not a full concurrency framework; it is a narrow statefile ownership check before writing advisory observation fields.
