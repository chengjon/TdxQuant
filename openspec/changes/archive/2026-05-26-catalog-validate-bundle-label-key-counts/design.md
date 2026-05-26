# Design: Catalog Validate Bundle Label Key Counts

## Behavior

The summary view builder already copies `bundle_label_counts` and `task_report_bundle_label_counts`. The new fields are computed as:

- `len(bundle_label_counts)`
- `len(task_report_bundle_label_counts)`

The fields appear only in `catalog validate --view summary` output and remain derived from already parsed, non-executing catalog validation data.

## Boundary

The fields count distinct label keys, not bundles. They do not expose complete manifests, prove entry availability, execute steps, or validate workflow semantics.

## Verification

- Add API CLI summary assertions comparing each key-count field to `len(<label_counts>)`.
- Run API CLI tests, OpenSpec validation, diff check, and the FUNCTION_TREE validator.
