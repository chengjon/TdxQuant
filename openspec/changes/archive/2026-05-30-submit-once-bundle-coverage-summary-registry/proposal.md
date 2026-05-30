## Why

The generic bundle boundary coverage rollup now applies to submit-once bundles as well as ordinary PingAn bundles. D-08 should explicitly register that read-only coverage surface so maintainers do not mistake the absence of registry evidence for missing functionality or, conversely, treat it as execution readiness.

## What Changes

- Add focused tests for submit-once bundle coverage-status rollups.
- Update D-08 FUNCTION_TREE evidence to cite `trade_plan_boundary_input_coverage_status_counts` for buy/sell submit-once bundles and selected ranges.
- Preserve D-08 as `[部分实现]`; this remains read-only catalog summary evidence only.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents submit-once bundle coverage-status summary behavior.
- `tdx-function-tree-registry`: D-08 evidence reflects submit-once bundle coverage-status summary without changing execution status.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
