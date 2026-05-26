# Design: Catalog plan step entry counts

## Context

Bundle plan/preview summary views are non-executing projections of selected resolved bundle steps. The selected `steps` list already contains per-step `entry` values. `step_entry_counts` makes that entry distribution available without forcing callers to iterate the step list.

`step_entry_key_count` is the cardinality hint for that map.

## Goals / Non-Goals

- Goal: expose `step_entry_counts` for bundle plan summary views.
- Goal: expose `step_entry_counts` for bundle preview summary views, including filtered step ranges.
- Goal: expose `step_entry_key_count` as `len(step_entry_counts)`.
- Non-goal: expose option values or resolved arguments beyond existing summary behavior.
- Non-goal: add these fields to detailed output.
- Non-goal: execute catalog entries, tasks, reports, trades, or bundle steps.

## Decisions

- Add a helper mirroring existing step source/name count helpers that counts non-empty string `entry` values.
- Derive both fields in `_build_catalog_summary_view()` only for bundle plan/preview summary views.
- Keep `selected_step_count` as the resolved selected-step total; `step_entry_key_count` only counts distinct entry names.

## Risks / Trade-offs

- The map can be mistaken for a full bundle manifest. The registry and spec state it is only a selected-step entry distribution and not execution coverage or readiness proof.

## Migration Plan

No migration required. Existing fields remain unchanged.

## Open Questions

None.

