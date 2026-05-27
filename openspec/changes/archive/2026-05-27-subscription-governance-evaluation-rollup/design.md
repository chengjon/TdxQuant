## Context

`watch-status --view summary` intentionally avoids raw control and watch payloads while surfacing compact runtime and governance projections. Recent work added `governance.decision_summary` so callers can inspect advisory decision metadata without treating it as an executable control instruction. The same pattern is useful for staleness evaluation metadata.

## Design

When a summary view includes governance metadata and `evaluation_summary` is a dictionary, add:

- `staleness_evaluated`
- `evaluated_count`
- `stale_count`
- `fresh_count`
- `not_evaluated_count`
- `primary_stale_component`
- `primary_fresh_component`
- `primary_not_evaluated_component`
- `has_stale_component`
- `has_fresh_component`
- `all_components_evaluated`

Boolean fields are derived from integer count fields. Missing or non-integer counts are treated conservatively as false for the derived booleans. Existing detailed `evaluation_summary` and other governance sibling fields remain unchanged.

## Non-Goals

- Do not change `build_subscription_watch_status_summary()` governance decisions or stale/fresh classification.
- Do not expose raw control/watch payloads, full reasons/actions beyond existing bounded samples, or event-stream data.
- Do not add reconnect/backoff/restart/lifecycle behavior, PID liveness checks, run ownership proof, or production governance strategy.
