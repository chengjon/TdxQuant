# catalog validate source summary design

## Design

`source_summary` is emitted only by catalog validation summary views. It is a compact rollup of already projected source-count metadata:

```json
{
  "entry_key_count": 0,
  "bundle_step_key_count": 2,
  "total_key_count": 2,
  "entry_count": 0,
  "bundle_step_count": 245,
  "has_entry_sources": false,
  "has_bundle_step_sources": true
}
```

Rules:

- `entry_key_count` mirrors `entry_source_key_count`.
- `bundle_step_key_count` mirrors `bundle_step_source_key_count`.
- `total_key_count` is derived from the union of keys in the projected `entry_source_counts` and `bundle_step_source_counts` maps.
- `entry_count` mirrors the selected entry validation count.
- `bundle_step_count` mirrors the selected resolved bundle-step count.
- Existing sibling fields remain available for compatibility.

## Boundaries

This change does not add source policy validation, source mutation, workflow building, scheduling, execution, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider calls, or bundle-step execution. It is an additive non-executing validation summary projection.
