# Design: Evaluated fields in subscription governance evaluation rollup

## Scope

This is an additive read-only projection change. It does not modify subscription-watch execution, stale threshold evaluation, reconnect/backoff/restart behavior, worker lifecycle, HTTP routes, SSE, or event-stream behavior.

## Field Semantics

Summary-view `governance.evaluation_rollup` SHALL derive:

- `primary_evaluated_component`: copied from `governance.evaluation_summary.primary_evaluated_component`.
- `has_evaluated_component`: true when `governance.evaluation_summary.evaluated_count` is a positive integer.

The implementation mirrors the existing rollup style: it derives boolean hints from numeric counts already present in `evaluation_summary` and copies primary-component fields from the detailed summary.

## Non-goals

- No new staleness calculation or threshold interpretation.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream execution.
- No exposure of raw `control`, `watch_status`, full reasons, or full actions in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.

