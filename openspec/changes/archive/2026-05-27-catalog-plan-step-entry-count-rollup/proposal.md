# catalog plan step entry count rollup

## Why

`catalog plan/preview --view summary` already computes selected bundle step entry counts at the top level and exposes entry key counts in compact rollups. Consumers that read only `selected_step_summary` or `plan_summary` still need to inspect the wider payload to see which entry ids are represented.

Adding the existing `step_entry_counts` map to the compact rollups keeps the catalog discovery surface self-contained while preserving the current non-executing catalog boundary.

## What Changes

- Add `selected_step_summary.step_entry_counts` derived from the already-computed selected step entry counts.
- Add `plan_summary.step_entry_counts` by forwarding the selected-step rollup field.
- Cover plan and preview summary output in `tests/test_api_cli.py`.
- Update `FUNCTION_TREE.md` E-11 evidence/boundary registration.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected tests: `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` E-11 supplemental evidence.
- No task, report, trade, bundle step, workflow, broker readiness, or execution behavior is added.

