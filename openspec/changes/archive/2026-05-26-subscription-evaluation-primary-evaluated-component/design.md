# Design: Subscription primary evaluated component

## Context

`build_subscription_watch_status_summary()` builds a read-only governance summary from heartbeat, watermark, and reconnect sub-summaries. `_build_subscription_watch_governance_evaluation_summary()` already maintains ordered `evaluated_components`, `stale_components`, `fresh_components`, and `not_evaluated_components`, plus primary hints for stale/fresh/not-evaluated lists.

## Goals / Non-Goals

- Goal: expose `primary_evaluated_component` as the first component in the existing `evaluated_components` list.
- Goal: return `None` when `evaluated_components` is empty.
- Goal: preserve existing evaluated/stale/fresh/not-evaluated counts and list ordering.
- Non-goal: change staleness thresholds or timestamp parsing.
- Non-goal: trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
- Non-goal: expose raw control/watch payloads in summary views.

## Decisions

- Add the field beside `evaluated_components` in the evaluation summary return object.
- Do not add a new helper because the value is a direct first-item projection.
- Rely on existing HTTP/CLI summary projection behavior, which deep-copies `evaluation_summary` when present.

## Risks / Trade-offs

- The new field is additive and should be ignored by older callers.
- The field is an identity hint, not a health or readiness guarantee.

## Migration Plan

No migration is required. Existing fields remain unchanged.

## Open Questions

None.
