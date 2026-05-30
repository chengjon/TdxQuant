## Why

D-07 bundle plan/preview summaries now expose trade boundary counts and command rollups. Maintainers also use `--from-step` / `--to-step` to inspect a selected range, and the summary should make it obvious whether the selected range contains any trade boundary without interpreting zero counts manually.

## What Changes

- Add additive `has_trade_plan_boundary` to catalog bundle `plan` and `preview` summary views.
- Cover PingAn bundle slices that include and exclude the trade step.
- Update D-07 FUNCTION_TREE evidence to cite selected-step boundary presence while preserving the `[部分实现]` status and non-execution boundaries.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents read-only selected-step trade-boundary presence for bundle summary views.
- `tdx-function-tree-registry`: D-07 evidence reflects selected-step boundary presence coverage without implying execution readiness.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
