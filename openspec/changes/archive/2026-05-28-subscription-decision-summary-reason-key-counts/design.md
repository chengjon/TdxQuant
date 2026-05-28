# Design: Reason key counts in subscription decision summary

## Scope

This change is an additive, read-only summary projection. It does not modify subscription-watch execution, governance decision logic, reconnect/backoff/restart behavior, worker lifecycle, HTTP routes, SSE, or event-stream behavior.

## Field Semantics

Summary-view `governance.decision_summary.reason_source_key_count` SHALL be copied from `governance.reason_summary.source_key_count`.

Summary-view `governance.decision_summary.reason_code_key_count` SHALL be copied from `governance.reason_summary.reason_code_key_count`.

These fields complement:

- `decision_summary.primary_reason`, which identifies the first advisory reason.
- `decision_summary.primary_reason_source`, which identifies the parsed reason source for the first advisory reason.
- `decision_summary.reason_count`, which counts total advisory reasons rather than unique source or code keys.

## Non-goals

- No new governance decision logic.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream execution.
- No exposure of raw `control`, `watch_status`, full reasons, or full actions in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.
