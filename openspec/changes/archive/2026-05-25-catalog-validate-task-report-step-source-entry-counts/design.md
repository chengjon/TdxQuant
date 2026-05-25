## Design

Extend `_validate_catalog_registry()` with a `task_report_bundle_step_source_entry_counts` map. For each selected resolved bundle that contains both task and report steps, iterate over resolved steps and count `f"{source}:{entry}"` when both values are non-empty strings.

This count is intentionally scoped to task/report bundles, matching the existing `task_report_bundle_step_*` rollups. It complements:

- `task_report_bundle_step_source_counts`
- `task_report_bundle_step_entry_counts`
- `task_report_bundle_step_source_name_counts`

`_build_catalog_summary_view()` will copy the map from validation into `summary_view`, following the existing summary projection pattern for adjacent task/report rollups.

## Boundaries

- The map is a validation summary, not an execution plan.
- It does not prove a task or report ran.
- It does not add workflow-builder behavior or trading readiness.
