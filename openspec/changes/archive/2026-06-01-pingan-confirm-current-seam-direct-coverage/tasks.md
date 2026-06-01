## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for direct confirm-current seam coverage.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add direct confirm-current seam tests for rejected gate, non-advanced dispatch, and advanced finalize.
- [x] 2.2 Run the focused new tests and confirm they fail before the test imports/coverage are wired.

## 3. Implementation

- [x] 3.1 Wire direct tests to the existing confirm-current seam exports.
- [x] 3.2 Update `FUNCTION_TREE.md` D-07 evidence and boundary for direct seam coverage.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
