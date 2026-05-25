## Why

B-16/E-09 long-run subscription status already exposes `evaluation_summary.component_status_counts`, but that map includes components whose stale thresholds were not evaluated. Maintainers need a compact way to distinguish the distribution of explicitly evaluated components from the default `not_evaluated` baseline.

Adding `evaluated_status_counts` keeps the summary precise while preserving the existing advisory-only boundary.

## What Changes

- Add `governance.evaluation_summary.evaluated_status_counts` to subscription long-run status summaries.
- Derive the counts only from heartbeat/watermark/reconnect components whose staleness is not `not_evaluated`.
- Preserve existing component lists, count fields, governance decisions, advisory actions, and lifecycle behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.

## Non-Goals

- No automatic reconnect, backoff, restart, scheduler, or lifecycle control.
- No change to stale threshold defaults.
- No replacement of `component_status_counts`; it continues to count all components.

