## Design

`_validate_catalog_registry()` already identifies selected resolved bundles that contain both `task` and `report` steps. During the existing task/report bundle loop, each step with a non-empty string `entry` will increment `task_report_bundle_step_entry_counts`.

The summary view will deep-copy this map beside the existing task/report bundle count fields.

The field is strictly aggregate evidence:

- it applies only to selected resolved bundles that include both task and report steps;
- the sum of values equals `task_report_bundle_step_count` for normalized steps with entries, matching the current runtime bundle shape;
- it does not expose full step payloads;
- it does not execute any catalog entry or bundle step.

## Risks

- The field overlaps with full selected `bundle_step_entry_counts`, but the new map is scoped to the task/report combo subset and therefore gives more precise E-11 registry evidence.

