# Design: Subscription governance evaluation rollup completeness

## Scope

This change is limited to additive, read-only summary projection fields. It does not modify the underlying subscription-watch controller, status evaluation semantics, reconnect/backoff behavior, worker lifecycle, HTTP routes, SSE/event-stream behavior, or command dispatch.

## Field Semantics

The summary-view `governance.evaluation_rollup` SHALL derive these fields from the existing `governance.evaluation_summary` object:

- `has_not_evaluated_component`: true when `not_evaluated_count` is a positive integer.
- `component_status_key_count`: copied from `evaluation_summary.component_status_key_count`.
- `evaluated_status_key_count`: copied from `evaluation_summary.evaluated_status_key_count`.

The fields intentionally mirror existing detailed summary semantics rather than recomputing staleness. If source fields are absent, the projection may return `null`/missing source values consistently with existing additive summary behavior.

## Non-goals

- No reconnect, backoff, restart, supervisor, lifecycle, HTTP, SSE, or event-stream execution.
- No changes to raw `status_summary.governance.evaluation_summary`.
- No new background worker process ownership or production-readiness claims.
- No promotion of B-16 or E-09 to `[已实现]`.

