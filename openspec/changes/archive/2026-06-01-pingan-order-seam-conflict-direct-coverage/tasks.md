## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for direct `reject_conflict` order seam coverage.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Coverage

- [x] 2.1 Add direct `execute_pingan_order` coverage for `reject_conflict`.
- [x] 2.2 Run the focused new test and confirm the branch contract.

## 3. Registry

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 evidence and boundary for conflict branch direct coverage.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
