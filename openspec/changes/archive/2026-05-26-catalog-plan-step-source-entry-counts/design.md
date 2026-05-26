# Design: Catalog plan step source-entry counts

## Context

The catalog bundle plan/preview summary path is a read-only projection built by `_build_catalog_summary_view()`. It reports selected step totals plus independent and source-qualified step distributions. Adding `source:entry` completes the compact non-executing source-qualified view for selected bundle steps.

## Goals / Non-Goals

- Goal: expose `step_source_entry_counts` for bundle plan summary views.
- Goal: expose `step_source_entry_counts` for bundle preview summary views, including filtered step ranges.
- Goal: expose `step_source_entry_key_count` as `len(step_source_entry_counts)`.
- Non-goal: expose option values, resolved arguments, or a complete bundle/step manifest.
- Non-goal: add these fields to detailed output.
- Non-goal: execute catalog entries, tasks, reports, trades, or bundle steps.

## Decisions

- Add a helper that counts `source:entry` pairs only when both fields are non-empty strings.
- Sort the resulting keys for stable JSON output.
- Derive both fields in `_build_catalog_summary_view()` only for bundle plan/preview summary views.
- Keep `selected_step_count` as the resolved selected-step total; `step_source_entry_key_count` only counts distinct source-qualified entries.

## Risks / Trade-offs

- The new fields are additive and should be ignored by older callers.
- The counts are metadata only; they do not imply workflow readiness or provider/broker availability.

## Migration Plan

No migration is required. Existing summary fields remain unchanged.

## Open Questions

None.
