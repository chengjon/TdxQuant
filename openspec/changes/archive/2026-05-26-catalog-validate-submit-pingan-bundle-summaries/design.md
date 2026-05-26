# catalog validate submit/PingAn bundle summaries design

## Design

`submit_once_bundle_summary` and `pingan_bundle_summary` are emitted only by catalog validation summary views. They are compact rollups of existing submit-once/PingAn bundle sibling fields and contain no option values, resolved args, full entry manifests, full bundle manifests, full step manifests, or executable instructions.

Shape:

```json
{
  "count": 14,
  "step_count": 32,
  "sample_count": 5,
  "sample_limit": 5,
  "sample_truncated": true,
  "label_key_count": 3,
  "step_source_key_count": 2,
  "step_name_key_count": 4,
  "step_source_name_key_count": 6,
  "step_entry_key_count": 4,
  "step_source_entry_key_count": 6,
  "step_option_key_count": 1,
  "step_source_option_key_count": 1
}
```

Rules:

- Counts are derived from existing summary sibling fields already projected by `catalog validate --view summary`.
- Existing sibling fields remain available for compatibility.
- The objects are emitted with zero/empty-derived values when the selected catalog has no matching submit-once or PingAn bundles.
- The objects are omitted from execution paths and do not execute catalog entries, tasks, reports, trades, or bundle steps.

## Boundaries

This change does not add a workflow builder, scheduler, execution engine, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, or bundle-step execution. It is an additive non-executing validation summary projection.
