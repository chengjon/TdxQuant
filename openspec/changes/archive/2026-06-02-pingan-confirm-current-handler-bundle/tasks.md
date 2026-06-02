# Tasks

## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for confirm-current handler bundle routing.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add a direct `execute_pingan_confirm_current(..., handlers=...)` test for the confirm-current handler bundle path.
- [x] 2.2 Run the focused new test and confirm it fails before implementation because the handler bundle is missing.

## 3. Implementation

- [x] 3.1 Add `PingAnConfirmCurrentExecutionHandlers` and `handlers=` compatibility to `execute_pingan_confirm_current(...)`.
- [x] 3.2 Route the manager confirm-current callsite through the grouped handler object.
- [x] 3.3 Preserve legacy individual callback arguments for existing direct callers.

## 4. Registry

- [x] 4.1 Update `FUNCTION_TREE.md` D-07 with status, evidence, and boundary for the handler-bundle increment.

## 5. Verification

- [x] 5.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Run `git diff --check`.
- [x] 5.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 5.5 Archive the OpenSpec change and repeat verification.
