## Context

The detailed `status_summary.governance` object carries full advisory internals, including `reasons` and `actions`. The compact summary view intentionally projects a smaller governance rollup: decision, review flag, staleness evaluation flag, advisory boundary, action summary, and evaluation summary.

After adding `governance.boundary`, the compact view now explains that governance is advisory-only. The remaining gap is bounded evidence about how many detailed reasons exist without exposing the detailed reason strings.

## Goals / Non-Goals

Goals:

- Derive `governance.reason_count` from the existing detailed `governance.reasons` list.
- Keep HTTP and CLI summary views in parity.
- Preserve reduced-view behavior by continuing to omit full reasons and actions.

Non-goals:

- Do not add a full governance reason list to compact views.
- Do not change governance decision, action, or evaluation calculations.
- Do not trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## Decisions

1. Derive count only from a list.

   If `governance.reasons` is present and is a list, summary builders add `reason_count = len(reasons)`. If it is absent or malformed, they omit `reason_count` rather than inventing a value.

2. Keep the field local to compact summary views.

   Detailed payloads already include `reasons`. The new field helps compact view consumers understand the omitted list size without changing the detailed contract.

3. Keep raw reasons out of compact views.

   Tests should assert that `reasons` and `actions` remain absent from summary governance payloads.

## Risks / Trade-offs

- Additive scalar output is low compatibility risk.
- A count does not explain exact reasons, but that is intentional; callers needing full detail should request the detailed payload.

## Migration Plan

No migration is required. Existing commands and HTTP calls continue to work.

## Open Questions

None.
