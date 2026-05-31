## 1. Contract

- [x] 1.1 Create OpenSpec proposal, design, and delta specs for guarded trade owner-lock guard forwarding.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add failing guarded task manager forwarding test.
- [x] 2.2 Add failing guarded CLI parser/dispatch forwarding tests.

## 3. Implementation

- [x] 3.1 Add lifecycle owner-lock guard parameters to `TdxTaskManager.guarded_trade_buy`.
- [x] 3.2 Add guarded CLI guard arguments and dispatch forwarding.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for guarded task/CLI and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
