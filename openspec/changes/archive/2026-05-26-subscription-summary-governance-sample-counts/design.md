# Design: Subscription governance sample counts

## Context

Detailed subscription watch status carries full governance internals, including raw reason and action lists. The compact HTTP/CLI summary view deliberately omits those lists and only exposes bounded samples, counts, summaries, limits, and truncation flags.

The current summary view has `reason_count`, `reason_samples`, `reason_sample_limit`, `reason_sample_truncated`, `action_count`, `action_samples`, `action_sample_limit`, and `action_sample_truncated`. Explicit sample counts make it easier for automation to compare visible samples with full counts without deriving lengths from arrays.

## Goals / Non-Goals

- Goal: expose `governance.reason_sample_count` as `len(reason_samples)` in HTTP and CLI summary views when reasons are present.
- Goal: expose `governance.action_sample_count` as `len(action_samples)` in HTTP and CLI summary views when actions are present.
- Non-goal: expose full `governance.reasons` or `governance.actions` in summary view.
- Non-goal: alter reconnect, backoff, restart, lifecycle, SSE, event-stream, or controller behavior.

## Decisions

- Derive counts from the already bounded sample arrays, not directly from raw lists, so the fields describe visible summary samples.
- Keep the existing full list counts (`reason_count`, `action_count`) unchanged.
- Mirror behavior in the HTTP helper and CLI helper because both build equivalent summary projections.

## Risks / Trade-offs

- The fields are additive and low risk, but could be confused with full counts. Naming them `*_sample_count` and keeping `*_count` unchanged preserves the distinction.

## Migration Plan

No migration required. Existing summary payload fields remain unchanged.

## Open Questions

None.
