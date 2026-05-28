# Design: Primary action fields in subscription decision summary

## Scope

This change is an additive summary projection. It does not modify subscription-watch execution, reconnect/backoff/restart behavior, worker lifecycle, HTTP routes, SSE, or event-stream behavior.

## Field Semantics

Summary-view `governance.decision_summary` SHALL derive:

- `primary_action`: copied from `governance.action_summary.primary_action`.
- `primary_action_reason`: copied from `governance.action_summary.primary_reason`.

The field name `primary_action_reason` is used instead of `primary_reason` to avoid ambiguity with `governance.reason_summary.primary_reason`.

## Non-goals

- No new governance decision logic.
- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream execution.
- No exposure of raw `control`, `watch_status`, full reasons, or full actions in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.

