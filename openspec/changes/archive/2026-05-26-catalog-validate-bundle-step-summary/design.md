## Design

`bundle_step_summary` is emitted only by catalog validation summary views. It is a compact rollup of existing selected-bundle sibling fields and contains no option values, resolved args, full bundle manifests, or executable instructions.

Shape:

```json
{
  "bundle_count": 54,
  "step_count": 108,
  "label_key_count": 4,
  "step_source_key_count": 3,
  "step_name_key_count": 12,
  "step_entry_key_count": 16,
  "step_source_name_key_count": 18,
  "step_source_entry_key_count": 20,
  "step_option_key_count": 10,
  "step_source_option_key_count": 14
}
```

Rules:

- Counts are derived from existing `bundle_*` and `bundle_step_*` sibling fields already projected in the summary view.
- Existing sibling fields remain available for compatibility.
- The object is omitted from execution paths and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## Boundaries

This change does not add a workflow builder, scheduler, execution engine, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, or bundle-step execution. It is an additive non-executing validation summary projection.
