## Context

The existing governance object contains detailed `reasons` and `actions`, plus
an additive `action_summary` and `staleness_evaluated` flag. CLI and HTTP
summary views intentionally omit full `governance.actions`, but operators still
benefit from a compact rollup that names which status components participated
in the staleness evaluation.

## Goals / Non-Goals

- Add `governance.evaluation_summary` to detailed long-run status summaries.
- Project `evaluation_summary` through opt-in CLI and HTTP summary views.
- Derive the rollup only from existing heartbeat, watermark, and reconnect staleness fields.
- Keep the feature advisory-only and read-only.
- Do not change reconnect/backoff scheduling, process lifecycle, HTTP control behavior, SSE, event streams, or raw detailed payload availability.

## Decisions

- Use component lists rather than booleans per component.
  - Rationale: `evaluated_components`, `stale_components`, and `not_evaluated_components` are compact and stable for summary consumers.
  - Alternative considered: add top-level `heartbeat_evaluated` style booleans. That would spread component-specific fields across the governance object.
- Treat any staleness other than `not_evaluated` as evaluated.
  - Rationale: existing summary behavior already uses that rule for `staleness_evaluated`.
- Keep full `governance.actions` omitted from summary views.
  - Rationale: summary views should remain compact and non-executing while detailed payloads preserve the full advisory list.

## Risks / Trade-offs

- The rollup may be mistaken for automated policy execution. Mitigation: specs and FUNCTION_TREE boundary explicitly state it is read-only/advisory and does not trigger reconnect/backoff/restart.
- The summary duplicates information available in sub-objects. Mitigation: the duplication is intentionally compact and bounded to three component names.

## Migration Plan

No migration is required. The new object is additive; existing detailed and summary consumers can ignore it.

## Open Questions

None.
