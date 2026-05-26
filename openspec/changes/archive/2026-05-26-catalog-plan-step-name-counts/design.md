# Design: Catalog plan step name counts

## Context

Bundle plan/preview summary views are non-executing projections of selected resolved bundle steps. The selected `steps` list already contains per-step names, but automation has to iterate that list to compute name distribution.

`step_name_counts` is a compact count map over selected step names. `step_name_key_count` is the cardinality hint for that map.

## Goals / Non-Goals

- Goal: expose `step_name_counts` for bundle plan summary views.
- Goal: expose `step_name_counts` for bundle preview summary views, including filtered step ranges.
- Goal: expose `step_name_key_count` as `len(step_name_counts)`.
- Non-goal: add these fields to detailed output.
- Non-goal: change selected step filtering, dispatch metadata, provenance, constraints, or catalog run behavior.
- Non-goal: execute catalog entries, tasks, reports, trades, or bundle steps.

## Decisions

- Add a helper mirroring `_build_catalog_step_source_counts()` that counts non-empty string step names.
- Derive both fields in `_build_catalog_summary_view()` only for bundle plan/preview summary views.
- Keep `selected_step_count` as the resolved selected-step total; `step_name_key_count` only counts distinct names.

## Risks / Trade-offs

- The map can be mistaken for a step manifest. The registry and spec explicitly state it is only a selected-step name distribution and not execution coverage.

## Migration Plan

No migration required. Existing fields remain unchanged.

## Open Questions

None.

