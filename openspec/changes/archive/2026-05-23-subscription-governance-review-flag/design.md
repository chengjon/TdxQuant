## Context

`build_subscription_watch_status_summary()` already computes a governance object from `overall_status`, heartbeat staleness, and watermark staleness. The governance object is advisory and currently includes `decision`, `reasons`, `actions`, `staleness_evaluated`, and `boundary`.

The existing `decision` value is stable, but callers that only need a boolean review gate must compare `decision == "manual_review"` themselves.

## Design

Inside `_build_subscription_watch_governance_summary()`:

- Build the existing `reasons` list.
- Compute `requires_manual_review = bool(reasons)`.
- Keep `decision = "manual_review"` when `requires_manual_review` is true, otherwise `observe`.
- Include `requires_manual_review` in the returned governance dict.

This is additive and does not change how reasons or actions are produced.

## Boundaries

- This does not trigger reconnect, backoff, restart, lifecycle, or event-stream behavior.
- This does not infer wall-clock staleness unless explicit thresholds are passed.
- Existing raw `control` and `watch_status` payloads remain unchanged.
