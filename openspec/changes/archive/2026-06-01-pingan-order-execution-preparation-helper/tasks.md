## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for PingAn order execution preparation locality.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Test

- [x] 2.1 Add focused coverage for the order execution preparation helper output.
- [x] 2.2 Run the focused new test and confirm it fails before the helper exists.

## 3. Implementation

- [x] 3.1 Add `PingAnOrderExecutionPreparation`.
- [x] 3.2 Add `_prepare_pingan_order_execution(...)` to `TdxTradeManager`.
- [x] 3.3 Route buy/sell/submit-once callsites through the preparation helper.
- [x] 3.4 Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
