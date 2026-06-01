## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for PingAn order dispatch options locality.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Test

- [x] 2.1 Add focused coverage for the order dispatch options object/helper output.
- [x] 2.2 Run the focused new test and confirm it fails before the options object exists.

## 3. Implementation

- [x] 3.1 Add `PingAnOrderDispatchOptions`.
- [x] 3.2 Add manager helper to build dispatch options from profile and callsite inputs.
- [x] 3.3 Route buy/sell/submit-once runner kwargs through the dispatch options object.
- [x] 3.4 Update `FUNCTION_TREE.md` D-08 evidence and boundary.

## 4. Verification

- [x] 4.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `git diff --check`.
- [x] 4.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 4.5 Archive the OpenSpec change and repeat verification.
