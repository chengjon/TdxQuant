## Design

`entry_summary` is emitted only by catalog validation summary views. It is a compact rollup of existing selected-entry sibling fields and contains no option values, resolved args, full entry manifests, full bundle manifests, or executable instructions.

Shape:

```json
{
  "count": 42,
  "source_key_count": 4,
  "label_key_count": 8
}
```

Rules:

- Counts are derived from existing `entry_count`, `entry_source_key_count`, and `entry_label_key_count` sibling fields already projected in the summary view.
- Existing sibling fields remain available for compatibility.
- The object is emitted for bundle-only selections with zero counts when no entries are selected.
- The object is omitted from execution paths and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## Boundaries

This change does not add a workflow builder, scheduler, execution engine, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, or bundle-step execution. It is an additive non-executing validation summary projection.
