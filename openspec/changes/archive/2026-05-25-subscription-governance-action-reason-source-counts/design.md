## Context

`build_subscription_watch_status_summary()` emits advisory governance actions only after existing explicit staleness or status checks produce reasons. The action summary is intentionally compact: it provides counts and primary action metadata while summary views omit the full `governance.actions` list.

The detailed governance object already has `reason_source_counts` based on reason prefixes. The new field mirrors that normalization inside `action_summary`, but counts the reasons attached to generated advisory actions rather than the raw `governance.reasons` list.

## Goals / Non-Goals

- Add a deterministic `governance.action_summary.reason_source_counts` object.
- Keep observe/default summaries empty when no advisory actions exist.
- Preserve summary-view behavior: include `action_summary`, continue omitting full `governance.actions`.
- Do not add reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
- Do not change how reasons or actions are generated.
- Do not treat the count as an execution queue, severity model, or automation policy.

## Decisions

- Source derivation reuses `_subscription_watch_governance_reason_source()` so action reason-source counts match `governance.reason_source_counts` naming.
- Counts are sorted by key before returning to keep JSON output deterministic.
- Missing or malformed action reasons fall back to the existing `unknown` source behavior through the shared helper.

## Risks / Trade-offs

- The field is partly redundant while every action maps one-to-one to one reason. That is acceptable because it keeps compact summary consumers from depending on full action lists.
- Future changes may allow multiple actions per reason. Counting action reasons inside `action_summary` remains semantically distinct from counting raw governance reasons.
