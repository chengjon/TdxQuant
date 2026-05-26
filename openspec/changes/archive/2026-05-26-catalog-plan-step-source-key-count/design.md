# Design: Catalog plan step source key count

## Context

Catalog bundle plan/preview summary views are non-executing projections of selected resolved bundle steps. They already include `step_source_counts`, which groups selected steps by source such as `task`, `report`, or `trade`.

`step_source_key_count` is a compact cardinality hint for that existing map. It does not count resolved steps and it does not expose step options or execute anything.

## Goals / Non-Goals

- Goal: expose `step_source_key_count` as `len(step_source_counts)` for bundle plan summary views.
- Goal: expose the same field for bundle preview summary views, including filtered step ranges.
- Non-goal: add this field to detailed output.
- Non-goal: change `step_source_counts`, `steps`, provenance, constraints, trade boundaries, or catalog run behavior.
- Non-goal: execute catalog entries, tasks, reports, trades, or bundle steps.

## Decisions

- Derive the key count immediately after building `step_source_counts` in `_build_catalog_summary_view()`.
- Keep the field only in summary views because detailed payloads already expose full selected-step details.
- Use the singular key-count name `step_source_key_count` to match existing summary naming for other count maps.

## Risks / Trade-offs

- The field can be confused with selected step count. The registry and spec state that it counts distinct map keys only; `selected_step_count` remains the resolved step count.

## Migration Plan

No migration required. Existing fields remain unchanged.

## Open Questions

None.

