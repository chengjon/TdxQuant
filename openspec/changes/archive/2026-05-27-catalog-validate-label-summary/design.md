# catalog validate label summary design

## Design

`label_summary` is emitted only by catalog validation summary views. It is a compact rollup of already projected label-count metadata:

```json
{
  "selected_label": "followup",
  "entry_key_count": 0,
  "bundle_key_count": 22,
  "total_key_count": 22,
  "selected_entry_count": 0,
  "selected_bundle_count": 115,
  "selected_total_count": 115,
  "has_selected_label": true
}
```

Rules:

- `entry_key_count` mirrors `entry_label_key_count`.
- `bundle_key_count` mirrors `bundle_label_key_count`.
- `total_key_count` is derived from the union of keys in the projected `entry_label_counts` and `bundle_label_counts` maps.
- `selected_entry_count`, `selected_bundle_count`, and `selected_total_count` are derived from the projected maps when `selected_label` is present; otherwise they are deterministic zero values.
- Existing sibling fields remain available for compatibility.

## Boundaries

This change does not add label policy validation, label mutation, workflow building, scheduling, execution, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider calls, or bundle-step execution. It is an additive non-executing validation summary projection.
