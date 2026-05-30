## Why

D-07 and D-08 now have extensive read-only catalog evidence, but that evidence is not enough to mark real PingAn trading as `[已实现]`. A separate promotion plan prevents FUNCTION_TREE from conflating discovery/summary support with live desktop trading readiness.

## What Changes

- Define promotion gates for D-07 buy/sell/confirm_current and D-08 submit_once before either node can move to `[已实现]`.
- Record an implementation order that starts with broker/environment ownership and safety gates, then desktop lifecycle/result evidence, then audit and acceptance evidence, and only then FUNCTION_TREE status transition.
- Update D-07/D-08 registry boundaries to cite the promotion plan while preserving `[部分实现]`.
- Do not implement live trading behavior in this change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-function-tree-registry`: require explicit evidence gates before D-07/D-08 status promotion.
- `tdx-desktop-trading-safety`: document safety and acceptance gates required before PingAn trading paths can be claimed implemented.

## Impact

- Affected registry: `FUNCTION_TREE.md`.
- Affected tests: `tests/test_function_tree_registry.py`.
- Verification: focused registry tests, OpenSpec strict validation, whitespace check, and FUNCTION_TREE registry validation.
