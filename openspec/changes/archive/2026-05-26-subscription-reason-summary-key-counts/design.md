# Design: Subscription reason summary key counts

## Context

`governance.reason_summary` is a compact rollup derived from advisory governance reasons. It carries primary reason metadata and two count maps:

- `source_counts`: reason prefix distribution.
- `reason_code_counts`: full advisory reason string distribution.

The new fields are cardinality hints for those maps. They are read-only diagnostics and do not change the underlying reason list or summary view truncation behavior.

## Goals / Non-Goals

- Goal: expose `source_key_count` as `len(source_counts)`.
- Goal: expose `reason_code_key_count` as `len(reason_code_counts)`.
- Goal: return zero key counts when no advisory reasons exist.
- Non-goal: expose full `governance.reasons` in compact summary view.
- Non-goal: change governance decision, staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Decisions

- Build the source and reason-code count maps once inside `_build_subscription_watch_governance_reason_summary()` and derive key counts from those maps.
- Keep the fields inside `reason_summary` because they describe the shape of existing reason-summary maps, not the top-level governance state.
- Preserve the existing compatibility alias `primary_reason_source`.

## Risks / Trade-offs

- Key counts can be mistaken for total reason counts. Naming them `*_key_count` and keeping `governance.reason_count` unchanged preserves the distinction.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.

