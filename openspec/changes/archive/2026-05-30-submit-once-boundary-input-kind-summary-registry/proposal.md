## Why

D-08 submit_once catalog plan/preview summaries already expose side and input coverage boundaries, but the FUNCTION_TREE registry does not yet cite the input-kind rollup that distinguishes submit_once order parsing from other PingAn trade boundaries. Registering this keeps D-08 precise without implying execution readiness.

## What Changes

- Add focused tests that buy/sell submit_once bundle summaries expose `trade_plan_boundary_input_kind_counts.submit_once_order=1`.
- Verify selected ranges excluding the trade step report an empty input-kind count map.
- Update D-08 evidence and boundary in `FUNCTION_TREE.md` while keeping D-08 `[部分实现]`.
- Preserve the boundary: this is non-executing catalog plan/preview summary evidence only.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-command-catalog`: register submit_once input-kind summary behavior for catalog plan/preview.
- `tdx-function-tree-registry`: register D-08 evidence and boundary wording for submit_once input-kind rollups.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
