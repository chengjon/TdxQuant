## Why

`FUNCTION_TREE.md` keeps B-16/E-09 subscription long-run governance as partial while the read-only status registry becomes more explicit. The current `governance.evaluation_summary` lists evaluated, stale, fresh, and not-evaluated components with separate counts, but it does not provide a compact count map that clients can compare without traversing multiple fields.

Adding `governance.evaluation_summary.component_status_counts` makes the heartbeat/watermark/reconnect staleness distribution explicit without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## What Changes

- Add additive `component_status_counts` to subscription governance `evaluation_summary`.
- Preserve summary view behavior by copying the existing `evaluation_summary` projection.
- Update tests and `FUNCTION_TREE.md` B-16/E-09 evidence/boundary.

## Non-Goals

- No new lifecycle control, supervisor behavior, reconnect scheduling, restart policy, or write behavior.
- No change to existing stale/fresh/not-evaluated classification.
- No expansion of summary views to include raw `control`, raw `watch_status`, full reasons, or full actions.
