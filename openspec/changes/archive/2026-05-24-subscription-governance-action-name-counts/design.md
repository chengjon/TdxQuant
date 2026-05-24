## Context

`build_subscription_watch_status_summary()` returns detailed subscription long-run governance data. The existing `governance.action_summary` is already derived from normalized advisory actions and is copied into CLI/HTTP summary views without exposing the full `governance.actions` list.

## Goals / Non-Goals

**Goals:**

- Add a deterministic `action_name_counts` object under `governance.action_summary`.
- Count only non-empty string `action` values from existing advisory action entries.
- Keep CLI/HTTP summary views as read-only projections.

**Non-Goals:**

- Do not add new governance actions, reconnect/backoff logic, restart behavior, lifecycle control, HTTP behavior, SSE behavior, or event-stream behavior.
- Do not expose the full `governance.actions` list in summary views.
- Do not interpret action counts as execution priority or automation policy.

## Decisions

- Extend `_build_subscription_watch_governance_action_summary()` rather than duplicating aggregation in view builders. This keeps the canonical detailed summary and read-only views consistent.
- Sort `action_name_counts` keys to keep JSON output deterministic for tests and operators.
- Return `{}` for observe/no-action states so absence of advisory actions is explicit without inventing placeholder action names.

## Risks / Trade-offs

- Extra summary surface could be mistaken for an automation plan. Mitigation: keep the field inside advisory `action_summary`, retain existing boundary text, and update `FUNCTION_TREE.md` to state that it is a derived count only.
- Action names may evolve later. Mitigation: derive from actual normalized action entries instead of hard-coding known action names.
