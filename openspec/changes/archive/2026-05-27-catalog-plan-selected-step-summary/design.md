## Context

Catalog bundle plan and preview summary views already include selected step counts, step source/name/entry counts, a bounded `steps` list, and non-execution constraints. The selected step window is present as sibling fields, but clients that need a compact view of the selected range must combine several fields themselves.

## Design

When `_build_catalog_summary_view()` handles bundle `plan` or `preview`, add `selected_step_summary` after the bounded `steps` list is built.

The object contains:

- `selected_from_step`
- `selected_to_step`
- `selected_step_count`
- `first_step_name`
- `last_step_name`
- `first_step_entry`
- `last_step_entry`
- `step_source_key_count`
- `step_name_key_count`
- `step_entry_key_count`
- `has_step_slice`
- `has_steps`

`has_step_slice` is true when either selected boundary is present. Existing `steps`, count maps, non-execution constraints, and `plan_outcome` remain unchanged.

## Non-Goals

- Do not change selected-step resolution or bundle slicing behavior.
- Do not expose raw bundle manifests beyond existing summary fields.
- Do not execute entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.
