## Context

`SubscriptionWatchBackgroundController.status()` returns raw control/watch status plus an additive `status_summary`. The heartbeat sub-object currently records `heartbeat_at` and presence, but it deliberately avoids wall-clock evaluation. B-16/E-09 now needs a narrow, testable step toward long-run governance: stale heartbeat diagnosis without changing worker lifecycle or reconnect/backoff behavior.

## Goals / Non-Goals

**Goals:**
- Preserve default `staleness=not_evaluated` behavior for callers that do not pass a threshold.
- Add explicit stale/fresh evaluation when `heartbeat_stale_after_seconds` is provided.
- Keep evaluation deterministic in tests by accepting an explicit `now_utc` value at the lower-level summary/controller API.
- Propagate the threshold through bridge HTTP and bridge CLI watch-status routes.

**Non-Goals:**
- No automatic reconnect, backoff, restart, process kill, or degraded-state mutation.
- No change to event stream/SSE behavior.
- No persisted artifact rewrite.
- No default wall-clock evaluation for existing callers.

## Decisions

1. Make stale evaluation opt-in.
   - Rationale: existing tests and callers expect projection-only status by default; automatic evaluation would make old fixture timestamps look stale.
   - Alternative considered: always evaluate with a default threshold. That would be a behavioral change and could confuse replay/offline status views.

2. Store evaluation results inside the existing heartbeat sub-object.
   - Rationale: heartbeat status, timestamp, age, and threshold belong together and remain additive.
   - Alternative considered: add a top-level `staleness` section. That would fragment heartbeat-specific fields.

3. Treat malformed timestamps as `invalid_timestamp` instead of failing the status request.
   - Rationale: status endpoints must remain diagnostic and tolerant of partial artifacts.
   - Alternative considered: return an error. That would make corrupted heartbeat timestamps hide other useful status fields.

## Risks / Trade-offs

- [Risk] Users may mistake stale diagnosis for automatic remediation. -> Boundary text and `FUNCTION_TREE.md` will state that reconnect/backoff behavior is unchanged.
- [Risk] Different clocks can produce different stale/fresh states. -> The API exposes `evaluated_at` and uses explicit `now_utc` in tests.
- [Risk] Query parameter validation could reject status requests. -> Only invalid threshold values fail; missing threshold keeps prior behavior.
