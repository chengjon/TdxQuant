# Design: Subscription governance hidden sample counts

## Context

Detailed subscription watch status carries full governance reason and action lists. The compact HTTP/CLI summary view deliberately omits those full lists and exposes bounded `reason_samples` / `action_samples`, visible sample counts, full list counts, limits, and truncation flags.

Explicit hidden sample counts make the truncation boundary easier to consume without requiring clients to calculate `reason_count - reason_sample_count` or `action_count - action_sample_count`.

## Goals / Non-Goals

- Goal: expose `governance.reason_sample_hidden_count` as the non-negative difference between the underlying reason list length and bounded visible reason samples.
- Goal: expose `governance.action_sample_hidden_count` as the non-negative difference between the underlying action list length and bounded visible action samples.
- Non-goal: expose full `governance.reasons` or `governance.actions` in summary view.
- Non-goal: change the sample limits or sample contents.
- Non-goal: alter reconnect, backoff, restart, lifecycle, SSE, event-stream, or controller behavior.

## Decisions

- Derive hidden counts from the same local values that already produce `reason_count`, `reason_sample_count`, `action_count`, and `action_sample_count`.
- Clamp differences to zero so mixed or non-string reason entries cannot produce a negative count if the visible sample logic changes later.
- Keep the fields inside `governance` next to the existing sample count, limit, and truncation metadata.

## Risks / Trade-offs

- The fields are additive and low risk, but naming must make clear they count items omitted from bounded samples, not unavailable detailed payload records.
- The count is summary metadata only; consumers needing full details must continue using the detailed view.

## Migration Plan

No migration required. Existing summary payload fields remain unchanged.

## Open Questions

None.
