## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for ordinary PingAn buy seam routing.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Test

- [x] 2.1 Add a focused `TdxTradeManager.pingan.buy(...)` manager test that expects seam delegation.
- [x] 2.2 Run the focused test and confirm it fails because ordinary buy has not delegated to the seam yet.

## 3. Implementation

- [x] 3.1 Route `TdxTradeManager.pingan.buy(...)` through `PingAnExecutionRequest` and `execute_pingan_order`.
- [x] 3.2 Preserve the existing desktop dispatch callback and all safety/finalize metadata.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07 evidence and boundary.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
