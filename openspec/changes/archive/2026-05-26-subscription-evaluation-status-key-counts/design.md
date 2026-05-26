# Design: Subscription evaluation status key counts

## Context

`status_summary.governance.evaluation_summary` already reports evaluated, stale, fresh, and not-evaluated component lists and counts. It also reports two status-count maps:

- `component_status_counts`: all governance components grouped by status.
- `evaluated_status_counts`: only explicitly evaluated components grouped by status.

The new fields are compact cardinality hints for those maps. They do not introduce a new status vocabulary and they do not decide health or lifecycle state.

## Goals / Non-Goals

- Goal: expose `component_status_key_count` as `len(component_status_counts)`.
- Goal: expose `evaluated_status_key_count` as `len(evaluated_status_counts)`.
- Goal: keep the fields available anywhere the detailed `evaluation_summary` is projected.
- Non-goal: change how heartbeat or watermark staleness is evaluated.
- Non-goal: replace existing component lists, scalar counts, or status-count maps.
- Non-goal: trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Decisions

- Derive the key counts in `_build_subscription_watch_governance_evaluation_summary()` from the same dictionaries used to build the count maps.
- Return `0` for `evaluated_status_key_count` when no component was explicitly evaluated.
- Keep the fields under `evaluation_summary` because they describe existing evaluation-map shape, not the top-level governance decision.

## Risks / Trade-offs

- The fields are additive and low risk, but readers could confuse key counts with component counts. The names include `key_count`, and the registry boundary states that component counts/maps remain authoritative.

## Migration Plan

No migration required. Existing status summary fields remain unchanged.

## Open Questions

None.

