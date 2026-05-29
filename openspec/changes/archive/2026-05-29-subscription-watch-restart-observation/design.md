## Context

B-16/E-09 is being advanced through small, evidence-backed lifecycle-control slices. The current system can persist a start request, execute an explicit restart, expose restart preflight, and show restartability in diagnostics. After a successful explicit restart, however, later status views do not retain a compact "run A was replaced by run B" observation.

## Goals / Non-Goals

**Goals:**

- Persist one compact latest successful explicit restart observation in the active control state.
- Return that observation in the restart response and project it into diagnostics views.
- Reuse existing `start_request` summary vocabulary so the observation stays small and stable.
- Keep all diagnostics projections read-only and derived from already fetched detailed status payloads.

**Non-Goals:**

- No automatic restart, restart queue, retry, reconnect, or backoff scheduler.
- No long-running supervisor loop or process ownership proof.
- No health/readiness assertion for the replacement provider beyond recording the successful controller start result.
- No restart history, audit ledger, or cross-process coordination beyond the existing active state file.

## Decisions

- Store `last_restart_observation` on the active replacement run's control payload only after `start()` succeeds. This keeps failed restart attempts from being mistaken for successful handoffs.
- Use a compact schema with `schema_version`, `status`, `previous_run_id`, `new_run_id`, `reason`, `stop_state`, `start_state`, `start_request_summary`, and a boundary string. This is enough for operator diagnostics without exposing raw stop/start payloads.
- Project the observation in diagnostics as `diagnostics.restart_observation`. This keeps it separate from `diagnostics.restartability`, which answers "can I restart now?" rather than "what happened last time?"
- Preserve the existing restart response fields and add the observation rather than changing the envelope.

## Risks / Trade-offs

- [Risk] A monkeypatched or future `start()` implementation may return success without writing active state. → The controller will still return the observation, but persistence is best-effort and tied to the replacement active state matching the new run id.
- [Risk] Operators may overread the observation as health/readiness proof. → The boundary string and FUNCTION_TREE entry explicitly state observation-only, no readiness or supervisor claim.
- [Risk] A single latest observation omits history. → This slice intentionally avoids restart history until there is a separate audit-ledger requirement.
