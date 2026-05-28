# Design: Reconnect governance rollup

## Scope

This change is additive and read-only. It summarizes existing reconnect diagnostics; it does not introduce restart/backoff scheduling, process ownership checks, supervisor loops, lifecycle control, provider lifecycle management, HTTP route changes, SSE changes, or event-stream behavior.

## Field Semantics

`governance.reconnect_rollup` SHALL be derived from the existing `reconnect` summary built by `build_subscription_watch_status_summary()`.

The rollup SHALL include:

- `staleness`: copied from `reconnect.staleness`.
- `reconnect_count`: copied from `reconnect.reconnect_count`.
- `consecutive_reconnect_failures`: copied from `reconnect.consecutive_reconnect_failures`.
- `has_reconnects`: true when `reconnect_count` is a positive non-boolean integer.
- `has_reconnect_failures`: true when `consecutive_reconnect_failures` is a positive non-boolean integer.
- `has_last_error`: true when `reconnect.last_error` is a non-empty object.
- `has_next_reconnect_at`: true when `reconnect.next_reconnect_at` is a non-empty string.
- `age_source`: copied from `reconnect.age_source`.
- `stale_after_seconds`: copied from `reconnect.stale_after_seconds`.

HTTP and CLI summary views SHALL copy `governance.reconnect_rollup` from the detailed governance payload when present.

## Non-goals

- No reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream execution.
- No process ownership or statefile lock ownership proof.
- No raw `control`, `watch_status`, full reasons, or full actions exposure in summary view.
- No promotion of B-16 or E-09 to `[已实现]`.
