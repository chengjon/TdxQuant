## Context

`_build_subscription_watch_governance_evaluation_summary()` already returns stable component lists and counts:

- `evaluated_components` / `evaluated_count`
- `stale_components` / `stale_count`
- `fresh_components` / `fresh_count`
- `not_evaluated_components` / `not_evaluated_count`

Existing tests assert these fields in the detailed status summary. This change registers that existing behavior in OpenSpec and FUNCTION_TREE.

## Goals / Non-Goals

- Goal: document the existing component list/count fields as an additive read-only contract.
- Goal: clarify that these fields are derived from explicit heartbeat/watermark/reconnect staleness evaluation only.
- Non-goal: changing status summary behavior, adding reconnect/backoff/restart automation, or treating these counts as health/readiness guarantees.

## Decisions

- Use a documentation/spec registration change instead of modifying code. The implementation and tests already expose the fields.
- Keep the field scope narrow to `governance.evaluation_summary`; do not introduce new top-level governance fields.
- Preserve the existing partial status in FUNCTION_TREE because long-run lifecycle governance remains outside this slice.

## Risks / Trade-offs

- Registration-only changes can look like no-op work. Mitigation: the value is closing a contract gap between implementation evidence and the single feature registry.
- Readers could interpret `stale_count` as automation readiness. Mitigation: boundary text explicitly says the fields do not trigger reconnect/backoff/restart or lifecycle control.

## Migration Plan

No runtime migration. The behavior already exists. Rollback removes only the registration/spec additions.

## Open Questions

None.
