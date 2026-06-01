## 1. Red Tests

- [x] 1.1 Add a controller test for rejecting process owner-gate access without process side effects.
- [x] 1.2 Add a controller test for recorded-PID guard rejection without process side effects.
- [x] 1.3 Run the new focused tests and confirm they fail before implementation.

## 2. Controller Implementation

- [x] 2.1 Add process lifecycle controller decision/result helpers.
- [x] 2.2 Route `TdxTradeManager.pingan.lifecycle_process(...)` through the controller for owner-gate and recorded-PID guard decisions.
- [x] 2.3 Preserve existing process execution and public result behavior.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-12 evidence and boundary.
- [x] 3.2 Run focused pytest and full `tests/test_trade_manager.py`.
- [x] 3.3 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.4 Archive the OpenSpec change.
- [x] 3.5 Re-run verification after archive.
- [x] 3.6 Commit only this slice.
