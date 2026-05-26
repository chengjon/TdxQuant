## Design

`task_report_bundle_summary` is emitted only by catalog validation summary views. It is a compact rollup of existing sibling fields and contains no option values, resolved args, full bundle manifests, or executable instructions.

Shape:

```json
{
  "count": 113,
  "step_count": 226,
  "sample_count": 3,
  "sample_limit": 3,
  "sample_truncated": true,
  "label_key_count": 6,
  "step_source_key_count": 2,
  "step_name_key_count": 12,
  "step_source_name_key_count": 18,
  "step_entry_key_count": 16,
  "step_source_entry_key_count": 20,
  "step_option_key_count": 10,
  "step_source_option_key_count": 14
}
```

Rules:

- Counts are derived from existing `task_report_bundle_*` sibling fields.
- Key counts are derived from the corresponding count maps already projected in the summary view.
- Existing sibling fields remain available for compatibility.
- The object is omitted from execution paths and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## Boundaries

This change does not add a workflow builder, scheduler, execution engine, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, or bundle-step execution. It is an additive non-executing validation summary projection.
