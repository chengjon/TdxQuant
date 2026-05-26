# Design: Subscription governance reason source key count

## Context

`governance.reason_source_counts` is already available in detailed status and in compact HTTP/CLI summary views. It is a source-prefix distribution for advisory governance reasons. `reason_summary.source_key_count` now describes the same map inside `reason_summary`; this change adds a top-level counterpart next to `reason_source_counts` for callers that read the top-level rollup.

## Goals / Non-Goals

- Goal: expose `governance.reason_source_key_count` as `len(governance.reason_source_counts)`.
- Goal: return `0` when no advisory reasons exist.
- Non-goal: expose full `governance.reasons` in compact summary view.
- Non-goal: replace `reason_summary.source_key_count`.
- Non-goal: change governance decisions, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Decisions

- Compute `reason_source_counts` once in `build_subscription_watch_status_summary()` and use it both for the existing map and the new key count.
- Keep the field top-level under `governance` because it describes the top-level `reason_source_counts` map that summary views already project.

## Risks / Trade-offs

- The field partially overlaps with `reason_summary.source_key_count`. The registry and spec state that it is only a top-level convenience hint and does not replace the nested reason summary.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.

