## Context

B-16/E-09 has explicit restart, restart preflight, restartability diagnostics, and latest restart observation. It still lacks a lifecycle behavior that changes restart decisions after failure. This slice adds only a bounded guard after a failed replacement start, which is enough to stop repeated manual restart attempts while leaving automatic supervision for a later design.

## Goals / Non-Goals

**Goals:**

- Persist a compact `restart_backoff` object after explicit restart replacement start fails.
- Return stable `RESTART_BACKOFF_ACTIVE` from `restart()` while the backoff window remains active.
- Surface the guard in `restart_preflight()` and diagnostics with stable `BACKOFF_ACTIVE` reason code.
- Keep backoff metadata small and derived from the explicit restart attempt.

**Non-Goals:**

- No automatic retry, scheduler, worker loop, or long-running supervisor.
- No provider health/readiness proof.
- No restart history or audit ledger.
- No PID/port ownership inference beyond existing background-control reconciliation.

## Decisions

- Store backoff on the active state file using `state="restart_backoff"` and `active=false`. This keeps the guard visible to existing status/preflight paths without inventing a separate statefile.
- Use a fixed bounded default backoff duration for this first slice. Configuration can be added later once the behavioral contract is proven.
- Check backoff before active-run validation in `restart()`. That makes repeated explicit restarts fail with `RESTART_BACKOFF_ACTIVE` rather than the less informative `NO_ACTIVE_RUN`.
- Include only compact fields: schema version, status, previous run id, reason, created/retry timestamps, backoff seconds, start error code, start request summary, and boundary.

## Risks / Trade-offs

- [Risk] A single fixed backoff duration may not fit every deployment. -> Keep it small and bounded; later work can add CLI/config control.
- [Risk] Operators may confuse the guard with automatic recovery. -> The boundary string and FUNCTION_TREE entry explicitly state that no retry/supervisor is scheduled.
- [Risk] A statefile-only guard can be manually removed. -> This is acceptable for an operator-controlled local lifecycle mechanism and avoids broader process ownership changes.
