## Context

`SubscriptionWatchBackgroundController.status()` currently returns raw `control` and `watch_status` payloads. The raw status already carries fields such as `heartbeat_at`, `event_count`, `last_sequence`, `last_event_ts`, `last_symbol`, `reconnect_count`, `last_disconnect_at`, `last_reconnect_at`, `next_reconnect_at`, `degraded_since`, and `last_error`. Bridge callers can read those fields, but they do not get a compact, stable projection that explains whether a long-running watch is healthy, stale, reconnecting, or degraded.

## Goals / Non-Goals

**Goals:**

- Add a deterministic `status_summary` projection to background status responses.
- Preserve existing raw `control` and `watch_status` payloads.
- Surface heartbeat, event watermark, reconnect, and degraded metadata in stable sub-objects.
- Keep the projection pure and testable without wall-clock freshness calculations.

**Non-Goals:**

- Do not implement a new reconnect/backoff scheduler.
- Do not mutate background process lifecycle behavior.
- Do not change bridge SSE/event-stream frame contracts.
- Do not infer heartbeat staleness from local wall clock in this package.

## Decisions

1. Build the summary inside `tdxquant/subscription_watch_background.py`.
   - Rationale: the controller is the source of truth that combines control-plane state and canonical run status.
   - Alternative considered: add summary only in `bridge_http.py`. Rejected because registry/in-process callers of the controller would miss the same stable projection.

2. Keep `control` and `watch_status` unchanged and add `status_summary`.
   - Rationale: compatibility matters for existing bridge clients and tests.
   - Alternative considered: replace raw fields with a reduced summary. Rejected because raw artifact compatibility is more important than payload compactness.

3. Avoid heartbeat age calculations.
   - Rationale: the stored status can be replayed or inspected offline. Wall-clock freshness belongs in a future package that defines clock source, timeout policy, and stale thresholds.

## Risks / Trade-offs

- Summary can look authoritative beyond its scope -> The payload includes a boundary field stating it is a projection only.
- Heartbeat presence is not the same as heartbeat freshness -> The heartbeat sub-object reports `present` or `missing`, not age/staleness.
- Reconnect metadata may be absent in old runs -> The summary must provide keys with `None` or zero defaults where appropriate.

## Migration Plan

No migration is required. Existing background status responses retain `control` and `watch_status`; `status_summary` is additive.

## Open Questions

- Clock-based stale heartbeat classification remains a future package.
- Backoff policy enforcement and retry scheduling remain a future package.
