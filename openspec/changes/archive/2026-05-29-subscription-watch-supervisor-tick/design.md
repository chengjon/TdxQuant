## Context

The recent restart backoff guard prevents repeated manual restart attempts after replacement start failure. To make that state actionable, an operator needs a safe single-step control operation that can decide "wait", "recover once", or "no actionable backoff" without creating a persistent supervisor.

## Goals / Non-Goals

**Goals:**

- Evaluate restart backoff state once per explicit call.
- Avoid calling `start()` while backoff is still active.
- Attempt exactly one replacement start when backoff has expired and the statefile still has a valid `start_request`.
- Surface stable result states through controller, HTTP, registry, and CLI.

**Non-Goals:**

- No daemon loop, scheduler, timer, retry worker, or automatic invocation.
- No new readiness or health assertion beyond the existing `start()` result.
- No PID/port ownership inference.
- No full restart history or audit ledger.

## Decisions

- Keep `supervisor_tick()` on `SubscriptionWatchBackgroundController` so it reuses existing start validation and active state writing.
- Persist the original `start_request` on restart-backoff control state. The compact `restart_backoff` metadata remains redacted; detailed control state already carries start metadata for restartability.
- Return `ok: true` for no-op wait/no-action decisions and `ok: false` for malformed recovery metadata or failed recovery start. This keeps actionable failures visible while making no-op ticks easy to poll manually.
- Expose HTTP as `POST /bridge/v1/watch/supervisor-tick` and CLI as `bridge watch-supervisor-tick` to make the operation explicitly operator-triggered.

## Risks / Trade-offs

- [Risk] This introduces one actual recovery action. -> It is only executed by explicit command/HTTP call and only once per call.
- [Risk] Persisting start_request in backoff state could be confused with exposing it in diagnostics. -> The compact backoff summary remains redacted; existing detailed control state is already a privileged lifecycle payload.
- [Risk] A failed tick can rewrite backoff repeatedly. -> That is intentional bounded behavior and still requires explicit operator calls.
