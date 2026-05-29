## Why

D-07 records PingAn buy/sell/confirm_current catalog entries and follow-up bundles as partially implemented. Bundle plan/preview summary views can already show per-step `trade_plan_boundary` and a boundary step count, but ordinary PingAn buy/sell/confirm_current bundles do not have a `side` field, so maintainers still need to scan the step array to know which trade command the selected bundle boundary represents.

## What Changes

- Add additive `trade_plan_boundary_commands` to catalog bundle `plan` and `preview` summary views.
- Cover `buy-pingan-complete-review`, `sell-pingan-complete-review`, and `confirm-current-pingan-complete-review` with focused tests.
- Update D-07 FUNCTION_TREE evidence to cite the command rollup while preserving its `[部分实现]` status and non-execution boundaries.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents read-only command rollups for selected bundle steps that expose `trade_plan_boundary`.
- `tdx-function-tree-registry`: D-07 evidence reflects compact, non-executing PingAn bundle boundary command summary coverage.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
