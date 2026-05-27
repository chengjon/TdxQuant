## Context

Catalog plan and preview summary views are intended to describe resolved entry or bundle plans without dispatching them. Existing fields already include target metadata, bounded key fields, step source/name/entry counts, and non-execution constraints. A compact outcome object can make that boundary easier to consume while preserving the detailed sibling fields.

## Design

Add a helper that derives `plan_outcome` from the already-built summary dictionary after `_copy_catalog_non_execution_metadata()` has copied `constraints`.

The object contains:

- `mode`
- `target_type`
- `target_name`
- `selected_step_count`
- `step_source_key_count`
- `ok`
- `code`
- `message`
- `execution_mode`
- `dispatch_executed`
- `non_execution`
- `has_steps`

`non_execution` is true only when the copied constraints report `execution_mode == "non_executing"` and `dispatch_executed is False`. Existing `constraints`, `steps`, count maps, and trade boundary metadata remain available.

## Non-Goals

- Do not change plan/preview resolution, selected-step slicing, or catalog validation behavior.
- Do not execute entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.
- Do not introduce a dynamic workflow builder or claim arbitrary combinations are supported.
