# catalog validate bundle summary design

## Design

`bundle_summary` is emitted only by catalog validation summary views. It is a compact rollup of already projected bundle metadata:

```json
{
  "selected_bundle": null,
  "selected_label": "followup",
  "count": 115,
  "step_count": 245,
  "sample_count": 5,
  "sample_limit": 5,
  "sample_truncated": true,
  "label_key_count": 22,
  "has_bundles": true,
  "has_selected_bundle": false
}
```

Rules:

- `count` mirrors `bundle_count`.
- `step_count` mirrors `bundle_step_count`.
- Sample fields mirror the bounded bundle sample metadata.
- `label_key_count` mirrors `bundle_label_key_count`.
- `has_bundles` is derived from `count > 0`.
- `has_selected_bundle` is derived from the presence of `selected_bundle`.
- Existing sibling fields and `bundle_step_summary` remain available for compatibility.

## Boundaries

This change does not add bundle mutation, bundle execution, workflow building, scheduling, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider calls, or bundle-step execution. It is an additive non-executing validation summary projection.
