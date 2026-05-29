## Why

D-08 already exposes buy/sell submit-once task entries and the catalog planner can summarize their non-executing `trade_plan_boundary` for both plan and preview. `FUNCTION_TREE.md` currently highlights only a subset of that read-only surface, so the registry underspecifies how `task-buy-submit-once` and `task-sell-submit-once` can be inspected without running the workflow.

## What Changes

- Add focused catalog plan/preview tests for `task-buy-submit-once` and `task-sell-submit-once` summary boundaries.
- Update D-08 registry evidence to cite buy/sell submit-once task plan/preview parity.
- Preserve D-08 as `[部分实现]`; this is not a new desktop primitive, not `catalog run` expansion, and not a broker readiness or trading safety claim.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents read-only plan/preview boundaries for buy/sell submit-once task entries.
- `tdx-function-tree-registry`: D-08 evidence reflects existing read-only catalog plan/preview coverage without changing execution status.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
