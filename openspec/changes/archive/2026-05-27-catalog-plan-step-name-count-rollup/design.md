# catalog plan step name count rollup design

## Design

The catalog plan summary builder already computes `step_name_counts` from the selected resolved steps and exposes `step_name_key_count` in compact rollups. This change copies the existing count map into:

```json
{
  "selected_step_summary": {
    "step_name_counts": {
      "confirm": 1,
      "audit": 1
    }
  },
  "plan_summary": {
    "step_name_counts": {
      "confirm": 1,
      "audit": 1
    }
  }
}
```

Rules:

- The count map is derived only from already-selected resolved catalog steps.
- The map is sorted by the existing helper before it reaches the summary rollups.
- `plan_summary.step_name_counts` mirrors `selected_step_summary.step_name_counts`.
- Missing selected-step metadata remains `None` rather than triggering extra resolution.

## Boundaries

This is a read-only catalog discovery projection. It does not execute task, report, trade, or bundle steps; it does not validate option values or workflow semantics; it does not prove broker readiness, trade safety, or execution coverage.

