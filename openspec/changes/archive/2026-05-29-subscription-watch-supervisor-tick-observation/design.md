## Context

`SubscriptionWatchBackgroundController.supervisor_tick()` is an explicit single-step operation over restart backoff state. It can wait, no-op, recover by starting one replacement run, or fail with a stable tick error. `supervisor_run()` already persists a compact aggregate `last_supervisor_run_observation`, and diagnostics already project that aggregate, but a direct manual tick has no persisted observation.

This change records only the latest compact tick observation. It intentionally does not introduce a scheduler, daemon loop, retry history, provider readiness proof, or raw payload persistence.

## Goals / Non-Goals

Goals:

- Persist one compact `last_supervisor_tick_observation` after explicit tick evaluation when an existing statefile is available.
- Avoid creating a lifecycle statefile solely to record a no-op tick when no restart backoff/control state exists.
- Project the compact observation through diagnostics view.
- Keep returned `supervisor_tick()` payloads backward-compatible.

Non-goals:

- No background supervisor loop, automatic retry, cron behavior, or long-running daemon.
- No provider lifecycle ownership or readiness assertion.
- No history ledger of tick attempts.
- No raw `restart_backoff`, raw `start_result`, raw `start_request`, logs, provider credentials, or file paths in the persisted diagnostics observation.

## Decisions

- Add schema version `tdx.subscription_watch.supervisor_tick_observation.v1`.
- Use boundary `observation_only;does_not_schedule_supervisor_or_background_retry`.
- Persist only on an existing active control payload. If no statefile exists, the no-op tick remains a returned result only.
- For successful tick results, derive observation fields from `result`: `status`, `decision`, `action_taken`, `reason_codes`, optional `previous_run_id`, optional `new_run_id`, and optional compact `start_request_summary`.
- For failed tick results, derive `status: failed`, `decision: failed`, `action_taken: false`, optional `error_code`, compact `reason_codes`, `reason`, and boundary from the stable error envelope.
- Diagnostics projection copies only the compact observation fields already persisted under `control.last_supervisor_tick_observation`.

## Risks / Trade-offs

- Persisting only the latest observation means older tick outcomes are overwritten. That is acceptable for this slice because the goal is a status/diagnostics register, not an audit trail.
- A recovered tick depends on `start()` writing a current active state. If a future start implementation changes that behavior, persistence remains best-effort and does not alter returned tick semantics.
- Keeping the observation compact avoids leaking lifecycle internals, but callers that need raw debug payloads must use existing direct command responses or logs.
