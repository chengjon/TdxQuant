## 1. Red Tests

- [x] 1.1 Add a public behavior test for a read-only task boundary method.
- [x] 1.2 Add a facade delegation test proving `TdxTaskManager` routes the selected read-only workflow through the boundary.
- [x] 1.3 Confirm the selected workflow does not dispatch desktop trade execution.

## 2. Boundary Implementation

- [x] 2.1 Introduce a read-only task boundary module under `tdxquant/api/`.
- [x] 2.2 Move or delegate the selected read-only workflow implementation into the boundary.
- [x] 2.3 Preserve existing `TdxTaskManager` public method signatures and result payloads.
- [x] 2.4 Keep desktop trade write/lifecycle workflows untouched.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` evidence and boundary for the task manager read-only boundary.
- [x] 3.2 Run focused task manager tests.
- [x] 3.3 Run `openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Run `python scripts/validate_function_tree_registry.py`.
- [x] 3.6 Archive the OpenSpec change and repeat verification.
