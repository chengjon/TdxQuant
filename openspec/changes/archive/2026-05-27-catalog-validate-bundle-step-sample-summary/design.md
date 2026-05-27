# catalog validate bundle-step sample summary design

## Design

Bundle validation will collect a bounded list of resolved bundle names that survived the existing `--kind`, `--bundle`, and `--label` filters. The sample list is projected only in validation summary views and is limited to a fixed internal cap.

Projected sibling fields:

```json
{
  "bundle_samples": ["buy-pingan-complete-review"],
  "bundle_sample_count": 5,
  "bundle_sample_limit": 5,
  "bundle_sample_truncated": true
}
```

Compact summary shape:

```json
{
  "bundle_count": 115,
  "step_count": 245,
  "sample_count": 5,
  "sample_limit": 5,
  "sample_truncated": true,
  "label_key_count": 22,
  "step_source_key_count": 2,
  "step_name_key_count": 7,
  "step_entry_key_count": 58,
  "step_source_name_key_count": 7,
  "step_source_entry_key_count": 58,
  "step_option_key_count": 1,
  "step_source_option_key_count": 1
}
```

Rules:

- Samples contain bundle names only, not full bundle manifests, full step manifests, option values, resolved args, or executable instructions.
- Samples are derived during existing read-only bundle resolution inside `catalog validate`; no catalog entry, task, report, trade, provider, or bundle step is executed.
- Existing sibling fields and family-specific summaries remain available for compatibility.
- Empty selections return deterministic zero/empty-derived sample metadata.

## Boundaries

This change does not add a workflow builder, scheduler, execution engine, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider call, or bundle-step execution. It is an additive non-executing validation summary projection.
