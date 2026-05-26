# Design: Catalog Validate Step Source Key Counts

## Behavior

The summary view builder already copies `bundle_step_source_counts` and `task_report_bundle_step_source_counts` from validation results. The new scalar fields are computed as:

- `len(bundle_step_source_counts)`
- `len(task_report_bundle_step_source_counts)`

The fields appear only in `catalog validate --view summary` output and remain derived from already parsed, non-executing catalog validation data.

## Boundary

The fields count distinct map keys, not steps. They do not expose full manifests, prove entry availability, execute steps, or validate option semantics.

## Verification

- Add API CLI summary assertions comparing each key-count field to `len(<source_counts>)`.
- Run API CLI tests, OpenSpec validation, diff check, and the FUNCTION_TREE validator.
