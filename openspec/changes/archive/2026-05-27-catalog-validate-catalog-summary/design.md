# catalog validate catalog summary design

## Design

`catalog_summary` is emitted only by catalog validation summary views. It is a compact top-level rollup of already projected validation summary fields:

```json
{
  "mode": "validate",
  "kind": "bundle",
  "selected_entry": null,
  "selected_bundle": null,
  "selected_label": "followup",
  "valid": true,
  "invalid_count": 0,
  "non_execution": true,
  "entry_count": 0,
  "bundle_count": 115,
  "bundle_step_count": 245,
  "label_key_count": 22,
  "source_key_count": 2,
  "has_entries": false,
  "has_bundles": true,
  "has_invalid_entries": false,
  "has_selected_label": true
}
```

Rules:

- Selection and validation fields mirror the existing validation summary fields.
- Entry, bundle, and bundle-step counts mirror existing compact summary siblings.
- Label and source key counts are derived from `label_summary.total_key_count` and `source_summary.total_key_count`.
- Presence flags are derived from already projected counts and compact summary objects.
- Existing sibling fields and compact summary objects remain available for compatibility.

## Boundaries

This change does not add catalog mutation, workflow building, scheduling, execution, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider calls, or bundle-step execution. It is an additive non-executing validation summary projection.
