# catalog plan step name count rollup

## Why

`catalog plan/preview --view summary` already computes selected bundle step name counts at the top level and exposes key counts in compact rollups. Consumers that only read `selected_step_summary` or `plan_summary` still have to look outside those compact objects to answer which step names are represented.

Adding the existing `step_name_counts` map to the compact rollups keeps the catalog discovery surface stable and self-contained without executing catalog steps or changing workflow behavior.

## What Changes

- Add `selected_step_summary.step_name_counts` derived from the already-computed selected step name counts.
- Add `plan_summary.step_name_counts` by forwarding the selected-step rollup field.
- Cover plan and preview summary output in `tests/test_api_cli.py`.
- Update `FUNCTION_TREE.md` E-11 evidence/boundary registration.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected tests: `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` E-11 supplemental evidence.
- No task, report, trade, bundle step, workflow, broker readiness, or execution behavior is added.

