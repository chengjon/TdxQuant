## Context

The action summary is the compact, summary-safe place for advisory action rollups. It already contains counts by severity, action name, and action reason source. The detailed payload retains full `governance.actions`, while summary views copy `action_summary` and omit the full action list.

The new field mirrors `governance.reason_summary.reason_code_counts`, but counts reason strings attached to generated advisory actions. This keeps action rollup semantics distinct from raw reason rollup semantics if future changes generate multiple actions for one reason.

## Goals / Non-Goals

- Add a deterministic `governance.action_summary.reason_code_counts` object.
- Keep observe/default summaries empty when no advisory actions exist.
- Preserve summary-view behavior: include `action_summary`, continue omitting full `governance.actions`.
- Do not add reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
- Do not change how reasons or actions are generated.
- Do not treat the count as an execution queue, policy, severity model, or action readiness proof.

## Decisions

- Count only non-empty string `reason` values from advisory action dictionaries.
- Sort result keys before returning for deterministic JSON output.
- Keep malformed or missing action reasons out of `reason_code_counts`; their source-level fallback remains represented by `reason_source_counts`.

## Risks / Trade-offs

- The field overlaps with `governance.reason_summary.reason_code_counts` while action generation remains one-to-one with reasons. The field still belongs in `action_summary` because compact action consumers should not depend on raw reasons or full actions.
