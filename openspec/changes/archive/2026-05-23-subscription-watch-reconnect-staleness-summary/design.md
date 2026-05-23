## Context

Subscription watch status already has a stable read-only `status_summary` with heartbeat, watermark, reconnect, and governance sections. Heartbeat and watermark freshness are evaluated only when callers pass explicit thresholds. Reconnect metadata currently includes counters and timestamps, but no comparable explicit threshold evaluation.

## Goals / Non-Goals

**Goals:**

- Evaluate reconnect/degraded state age only when a caller supplies `reconnect_stale_after_seconds`.
- Reuse the existing staleness vocabulary and advisory governance shape.
- Preserve detailed status payloads and existing default behavior.

**Non-Goals:**

- Do not implement reconnect scheduling, backoff, restart, daemon supervision, or lifecycle changes.
- Do not infer reconnect staleness when the threshold is omitted.
- Do not turn advisory governance output into executable control decisions.

## Decisions

- Evaluate reconnect staleness from the first available resilience timestamp: `last_disconnect_at`, then `degraded_since`. This reflects how long the current reconnect/degraded posture has been visible without depending on scheduler internals.
- Add `reconnect.staleness=not_evaluated` by default. With a positive threshold, produce `fresh`, `stale`, `missing`, `invalid_timestamp`, `invalid_threshold`, or `not_applicable` as appropriate.
- Extend governance to consider reconnect staleness alongside heartbeat and watermark. A stale reconnect input adds `reconnect:stale` and a review-only action.
- Thread the new threshold through the same CLI, bridge registry, and HTTP surfaces that already carry heartbeat/watermark thresholds.

## Risks / Trade-offs

- `last_disconnect_at` and `degraded_since` may be absent in older artifacts. The summary reports `missing` under explicit evaluation rather than inventing a timestamp.
- `not_applicable` for non-resilience states means callers can pass a threshold safely without creating manual-review noise for healthy or stopped states.
- This remains a projection over existing artifacts, so it cannot prove that a reconnect loop is running.
