## Design

Extend `_validate_catalog_registry()` with `bundle_step_source_entry_counts`. For every selected resolved bundle step, count `f"{source}:{entry}"` when both values are non-empty strings.

This general selected-bundle rollup complements:

- `bundle_step_source_counts`
- `bundle_step_entry_counts`
- `bundle_step_source_name_counts`
- `task_report_bundle_step_source_entry_counts`

`_build_catalog_summary_view()` will copy the map into `summary_view` next to the adjacent selected-bundle step rollups.

## Boundaries

- The map is a validation summary only.
- It does not include full step definitions or option values.
- It does not execute entries, tasks, reports, trades, or bundle steps.
