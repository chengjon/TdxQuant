## Design

Extend `_build_subscription_watch_governance_evaluation_summary()` to include `primary_fresh_component`. The value is the first item from the existing `fresh_components` list when any component is explicitly fresh, otherwise `None`.

The field is derived from current evaluation output rather than recalculating staleness. That keeps ordering and semantics consistent with `fresh_components`, `fresh_count`, and `evaluated_status_counts`.

## Boundaries

- This is a compact advisory hint, not a health guarantee.
- It does not expose raw control/watch payloads or raw governance arrays.
- It does not trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream changes.

