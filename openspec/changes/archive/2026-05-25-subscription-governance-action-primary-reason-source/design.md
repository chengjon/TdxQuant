## Context

`_build_subscription_watch_governance_action_summary()` already exposes primary action metadata and aggregate advisory action counts. It also computes reason-source counts for all advisory actions. The missing compact field is the source of the first advisory action reason.

## Goals / Non-Goals

- Add a deterministic `primary_reason_source` scalar to `governance.action_summary`.
- Use the existing `_subscription_watch_governance_reason_source()` helper.
- Keep detailed `governance.actions` hidden from summary views.
- Do not change reason generation, action generation, reconnect/backoff behavior, lifecycle behavior, HTTP handlers, SSE, or event-stream behavior.

## Decisions

- Derive `primary_reason_source` from `first_action["reason"]` when the first action exists.
- Return `None` when no action exists or no primary reason exists.
- Keep `reason_source_counts` unchanged as the aggregate view.

## Risks / Trade-offs

- The field can be mistaken for an action execution source. Boundary text will state that it is only a parsed prefix of an advisory reason string.
