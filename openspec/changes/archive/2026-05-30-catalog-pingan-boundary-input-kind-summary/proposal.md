## Why

D-07 already registers PingAn buy/sell/confirm_current catalog plan and preview boundary evidence, but maintainers cannot yet see a stable top-level summary of what input kind each trade boundary represents. Adding input-kind counts makes the read-only boundary clearer without implying broker readiness or execution.

## What Changes

- Add `trade_plan_boundary_input_kind_counts` to catalog plan/preview summary rollups for selected bundle steps.
- Project the field consistently at the top level, `selected_step_summary`, and `plan_summary`.
- Add focused tests for PingAn buy/sell/confirm_current bundles and selected-step slices.
- Update D-07 in `FUNCTION_TREE.md` while keeping it `[部分实现]`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-command-catalog`: expose read-only input-kind counts for trade plan boundaries in catalog plan/preview summary output.
- `tdx-function-tree-registry`: register D-07 evidence and boundary wording for the input-kind rollup.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
