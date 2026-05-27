# catalog plan summary design

## Design

`plan_summary` is emitted only by catalog plan and preview summary views. It is a compact top-level rollup of already projected planning metadata:

```json
{
  "mode": "plan",
  "target_type": "bundle",
  "target_name": "confirm-complete-review",
  "execution_mode": "plan",
  "non_execution": true,
  "dispatch_executed": false,
  "ok": true,
  "code": "ok",
  "selected_from_step": 0,
  "selected_to_step": 2,
  "selected_step_count": 3,
  "step_source_key_count": 2,
  "step_name_key_count": 3,
  "step_entry_key_count": 3,
  "step_resolved_arg_key_count": 1,
  "step_source_resolved_arg_key_count": 1,
  "has_steps": true,
  "has_step_slice": false
}
```

Rules:

- Target, execution, ok/code, and non-execution fields mirror `plan_outcome`.
- Selected range and step-count fields mirror `selected_step_summary` or already projected sibling fields.
- Key-count fields mirror `selected_step_summary` fields.
- Existing sibling fields, `plan_outcome`, and `selected_step_summary` remain available for compatibility.

## Boundaries

This change does not add workflow building, workflow execution, scheduling, broker readiness proof, trade safety proof, option-value validation, resolved-args disclosure, task/report execution, trade execution, provider calls, or bundle-step execution. It is an additive non-executing planning summary projection.
