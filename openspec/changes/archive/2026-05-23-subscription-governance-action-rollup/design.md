## Context

The existing governance summary includes:

- `decision`
- `requires_manual_review`
- `reasons`
- `actions`
- `staleness_evaluated`
- an advisory-only boundary string

`actions` is already machine-readable, but consumers that only need a compact status must inspect the full list.

## Goals / Non-Goals

**Goals:**

- Add an additive `governance.action_summary` object.
- Keep the rollup derived from existing actions and reasons.
- Preserve current advisory-only semantics.

**Non-Goals:**

- Trigger reconnect, restart, backoff, or lifecycle changes.
- Change existing action entries.
- Add new bridge routes, CLI flags, or event-stream fields outside the existing status payload.

## Decisions

- Add `action_summary` inside the existing governance object so all governance metadata stays together.
- Use `count`, `primary_action`, `primary_reason`, and `severity` fields:
  - `count` is the number of advisory actions.
  - `primary_action` and `primary_reason` come from the first action, or `null` when no actions exist.
  - `severity` is `none` when no actions exist, otherwise the first action severity.
- Derive the rollup after building actions, so it cannot drift from the existing action list.

## Risks / Trade-offs

- This is still not a full long-run governance engine. The rollup intentionally summarizes advisory output only and does not automate remediation.
