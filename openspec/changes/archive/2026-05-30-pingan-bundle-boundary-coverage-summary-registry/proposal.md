## Why

D-07 bundle plan/preview summaries now expose whether selected steps contain trade boundaries and which trade commands appear. The remaining scanability gap is input coverage status: maintainers must inspect individual step boundaries to see whether selected trade steps are missing required inputs or have no required inputs.

## What Changes

- Add additive `trade_plan_boundary_input_coverage_status_counts` to catalog bundle `plan` and `preview` summary views.
- Cover PingAn buy and confirm-current bundles, plus a selected range with no trade boundary.
- Update D-07 FUNCTION_TREE evidence to cite the coverage rollup while preserving partial status and non-execution boundaries.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents read-only input coverage status rollups for selected bundle trade boundaries.
- `tdx-function-tree-registry`: D-07 evidence reflects compact non-executing coverage-status summary for PingAn bundle plan/preview.

## Impact

- Affected code: `tdxquant/cli.py`.
- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
