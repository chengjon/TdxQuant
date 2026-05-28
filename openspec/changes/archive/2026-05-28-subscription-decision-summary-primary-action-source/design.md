# Design: Primary action reason source in subscription decision summary

## Scope

This change is an additive, read-only summary projection. It does not modify subscription-watch execution, governance decision logic, reconnect/backoff/restart behavior, worker lifecycle, HTTP routes, SSE, or event-stream behavior.

## Field Semantics

Summary-view `governance.decision_summary.primary_action_reason_source` SHALL be copied from `governance.action_summary.primary_reason_source`.

The field is intentionally named `primary_action_reason_source` to distinguish it from the existing `decision_summary.primary_reason_source`, which reflects `governance.reason_summary.primary_reason_source`.

## Non-goals

- No new governance decision logic.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream execution.
- No exposure of raw `control`, `watch_status`, full reasons, or full actions in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.

