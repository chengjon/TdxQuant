## Why

D-08 now records submit-once task entry plan/preview boundaries, and bundle plan/preview already exposes per-step `trade_plan_boundary` for selected buy/sell submit-once bundles. Maintainers still need a compact read-only summary that answers whether a selected bundle contains trade-boundary steps and which submit-once side is represented, without scanning the full step array or implying execution readiness.

## What Changes

- Add additive `trade_plan_boundary_step_count` and `trade_plan_boundary_sides` fields to catalog bundle `plan` and `preview` summary views.
- Cover `buy-submit-once-pingan-complete-review` and `sell-submit-once-pingan-complete-review` with focused red-first tests.
- Update D-08 FUNCTION_TREE evidence to cite the new bundle boundary rollup and preserve the existing partial status and safety boundaries.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents bundle plan/preview summary rollups for selected trade-boundary steps.
- `tdx-function-tree-registry`: D-08 evidence reflects compact, non-executing submit-once bundle boundary summary coverage.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
