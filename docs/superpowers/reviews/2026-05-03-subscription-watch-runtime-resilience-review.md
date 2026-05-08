# Review: Subscription Watch Runtime Resilience Design

Reviewed: 2026-05-03
Target: `docs/superpowers/specs/2026-05-03-subscription-watch-runtime-resilience-design.md`

## Summary

Design direction is sound: same `run_id` identity preservation, bounded fast reconnect, degraded low-frequency probe, and unchanged layer boundaries. The incremental relationship with existing artifact contracts is clear. Findings below are grouped by severity.

---

## Issues (should fix)

### I-1. `last_event_at` overlaps existing `last_event_ts` / `updated_at`

Current `status.json` already contains `last_event_ts` (see `subscription_watch_run.py:98`) and `updated_at`. The proposed `last_event_at` is nearly identical in semantics to `last_event_ts`.

Recommendation: either clarify that `last_event_at` IS `last_event_ts` (reuse the name), or define a distinct semantic difference. Introducing a synonym creates ambiguity at implementation time.

### I-2. `runtime_health` is redundant with `state`

`runtime_health` values (`ok / reconnecting / degraded`) map 1:1 to `state` values (`running / reconnecting / degraded`). Meanwhile `starting` and `stopping` have no corresponding `runtime_health` value.

Recommendation: pick one:
- Drop `runtime_health` entirely — readers use `state` directly.
- Give `runtime_health` an independent axis (e.g. `ok / degraded / unhealthy`) that does not mirror `state`.

### I-3. `reconcile_background_state` not covered for new states

`subscription_watch_background.py:119-179` (`reconcile_background_state`) currently recognizes only `starting / running / stopping / failed / stopped / completed`. Adding `reconnecting` and `degraded` creates a gap: if the worker process is killed while in `reconnecting` or `degraded`, the reconcile function falls through to the default branch and returns the raw payload without marking it as `failed`. This produces a zombie state visible to master.

The design should specify:
- Whether `reconnecting`/`degraded` crash semantics map to `failed` (recommended).
- Whether `active.json` state is kept in sync with `status.json` state, or they diverge.

### I-4. `degraded` stop-signal cleanup path undefined

The state transition diagram (line 119) shows `running|reconnecting|degraded -> stopping`, but the `degraded` stop path has a special requirement: the low-frequency probe timer must be interrupted and cleaned up. This cleanup path is not described.

---

## Gaps (should address)

### G-1. Concrete backoff parameters missing

The design says "short backoff retry" and "every 30s/60s probe" but provides no concrete values for v1:
- Fast reconnect: how many attempts? What interval?
- Degraded probe: fixed interval or increasing?
- Is there a hard upper bound on total reconnect time (e.g. after 24h, give up)?

Recommendation: provide default values for v1, even if configurable later.

### G-2. Disconnection detection mechanism not described

The design does not explain how the runner detects subscription unavailability. Is it a callback exception? A heartbeat timeout? An explicit error code from the runtime? This determines where the reconnect entry point lives in code and how to test it.

### G-3. `reconnect_metadata` role in event rows unclear

Current `events.jsonl` hardcodes `reconnect_metadata` to `{}` (`subscription_event.py:72`). The design says no synthetic lifecycle events in v1, but does not state whether events produced after a successful reconnect should populate `reconnect_metadata` (e.g. with reconnect count or recovery timestamp). If v1 keeps `{}`, confirm explicitly.

### G-4. `degraded_duration_ms` accumulation semantics undefined

`summary.json` adds `degraded_duration_ms`, but the runner must track each entry/exit from `degraded` to compute this. If a single run has multiple `degraded -> running -> degraded` cycles, is `degraded_duration_ms` cumulative or the last duration only?

### G-5. Fixture impact not addressed

Existing replay fixtures (`subscription-watch-status-completed`, `subscription-watch-summary-completed`) will encounter new fields. The design should confirm:
- Whether new fields are optional (existing fixtures remain valid as-is).
- Whether new fixture variants are needed (e.g. `subscription-watch-status-with-reconnect`).

---

## Suggestions (optional)

### S-1. `next_reconnect_at` becomes stale on stop

`next_reconnect_at` points to a future probe time, but if the runner enters `stopping` while in `degraded`, this field will reference a time that never arrives. Consider clearing it to `null` on `stopping`.

### S-2. `last_error` could include `consecutive_reconnect_failures`

Adding the current failure count to `last_error` (alongside `code / message / at`) saves cross-referencing two fields during debugging.

### S-3. Document `stopping` ownership explicitly

`stopping` exists in the current background controller but is not new. The design should note that `stopping` is driven by the background controller (external signal), not by the foreground runner itself — unlike `reconnecting`/`degraded` which are self-initiated.

---

## Finding Summary

| Category | Count | Severity |
|----------|-------|----------|
| Issues (should fix) | 4 | Medium-High |
| Gaps (should address) | 5 | Medium |
| Suggestions (optional) | 3 | Low |

Top two priorities:

1. **I-3**: `reconcile_background_state` crash semantics for new states must be defined — without it, zombie states are inevitable.
2. **I-1**: `last_event_at` naming collision with existing `last_event_ts` must be resolved before implementation begins.
