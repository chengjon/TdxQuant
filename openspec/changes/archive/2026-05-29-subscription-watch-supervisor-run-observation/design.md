## Context

`last_restart_observation` already records successful explicit restart handoff. `supervisor_run()` is a higher-level bounded foreground operation that may wait, recover, no-op, or stop on a failed tick. Capturing the latest compact observation makes the lifecycle state auditable without introducing a log stream or daemon.

## Goals / Non-Goals

**Goals:**

- Persist the latest supervisor-run observation when an existing control statefile can be updated.
- Include schema version, status, final decision, tick count, max ticks, interval, reason, action flag, tick status counts, tick decision counts, and optional handoff IDs.
- Project the observation through diagnostics view.
- Avoid raw `tick_summaries`, raw `start_result`, raw `start_request`, logs, or file paths in diagnostics.

**Non-Goals:**

- No supervisor history ledger.
- No background daemon, scheduler, timer, service manager, or automatic retry.
- No change to supervisor-run stop/continue semantics.
- No provider health/readiness/process ownership proof.
- No task/report/trade/workflow execution.

## Decisions

- Persist only a compact observation, not the full `supervisor_run()` result.
- Update the current active/control statefile if it exists. Do not create a new statefile merely to record a no-op observation when there is no lifecycle state.
- If a run recovers and `supervisor_tick()` starts a new active run, persist the observation onto the new active control state when possible.
- Diagnostics copies only a compact allowlist from `last_supervisor_run_observation`.

## Risks / Trade-offs

- [Risk] Observation may be absent after no-op with no statefile. -> That is intentional; diagnostics should not create lifecycle state.
- [Risk] Compact counts may be mistaken for a full audit. -> Boundary explicitly says latest observation only, not a history ledger.
- [Risk] Persisting after recovery can race with active state changes. -> The existing control-state write pattern already handles latest observation fields best-effort.

