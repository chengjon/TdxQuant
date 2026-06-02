# Tasks

## 1. Specification

- [x] 1.1 Add `tdx-desktop-trading-management` delta spec for order dispatch runner kwargs selection.
- [x] 1.2 Validate the OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add a focused dispatch-options test for `runner_kwargs(fast_inputs=False/True)`.
- [x] 2.2 Run the focused test and confirm it fails before implementation because `runner_kwargs` is missing.

## 3. Implementation

- [x] 3.1 Add `PingAnOrderDispatchOptions.runner_kwargs(...)` while preserving `base_kwargs(...)` and `fast_kwargs(...)`.
- [x] 3.2 Route buy/sell/submit-once manager callsites through `runner_kwargs(...)`.

## 4. Registry

- [x] 4.1 Update `FUNCTION_TREE.md` D-08 with status, evidence, and boundary for the runner-kwargs increment.

## 5. Verification

- [x] 5.1 Run focused PingAn trade manager/execution/gateway tests.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Run `git diff --check`.
- [x] 5.4 Run `python scripts/validate_function_tree_registry.py`.
- [x] 5.5 Archive the OpenSpec change and repeat verification.
