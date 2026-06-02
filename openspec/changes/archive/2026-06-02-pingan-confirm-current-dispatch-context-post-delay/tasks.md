# Tasks

## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for confirm-current dispatch context post-delay ownership.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add a focused preparation test asserting `dispatch_context.confirm_post_delay` is resolved from the effective profile.
- [x] 2.2 Run the focused test and confirm it fails before implementation because the context field is missing.

## 3. Implementation

- [x] 3.1 Add `confirm_post_delay` to `PingAnConfirmCurrentDispatchContext` with internal compatibility for existing constructors.
- [x] 3.2 Populate `confirm_post_delay` in `_prepare_pingan_confirm_current_execution(...)`.
- [x] 3.3 Route confirm-current click post-delay through `dispatch_context.confirm_post_delay`.

## 4. Registry

- [x] 4.1 Update `FUNCTION_TREE.md` D-07 with status, evidence, and boundary for the dispatch-context post-delay increment.

## 5. Verification

- [x] 5.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Run `git diff --check`.
- [x] 5.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 5.5 Archive the OpenSpec change and repeat verification.
