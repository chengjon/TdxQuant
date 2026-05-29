## Why

D-07 already has stable PingAn `buy` / `sell` / `confirm_current` task entries, and `catalog plan --view summary` can project non-executing `trade_plan_boundary` for more than the currently highlighted `task-sell` case. `FUNCTION_TREE.md` still under-documents the D-07 read-only plan surface by naming `task-sell` but not `task-buy` or `task-confirm-current`, so readers can miss that buy and confirm-current are also discoverable and bounded without executing a trade.

## What Changes

- Add focused catalog plan tests for `task-buy` and `task-confirm-current` summary boundaries.
- Update D-07 registry evidence to mention the aligned `task-buy` / `task-sell` / `task-confirm-current` non-executing plan coverage.
- Preserve D-07 as `[部分实现]` because direct trading execution, full broker readiness, and all desktop exception branches remain bounded.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`: documents that PingAn task buy/sell/confirm-current entries expose non-executing catalog plan boundaries.
- `tdx-function-tree-registry`: D-07 evidence reflects the existing read-only catalog plan coverage without claiming execution readiness.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_function_tree_registry.py`.
- Verification: focused API CLI and registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
