## 1. Contract

- [x] 1.1 Create OpenSpec proposal, design, and delta specs for task-level execution owner-lock guard forwarding.
- [x] 1.2 Validate the active OpenSpec change before implementation.

## 2. Red Tests

- [x] 2.1 Add failing task manager tests for trade-buy/trade-sell/trade-submit-once guard forwarding.
- [x] 2.2 Add failing CLI parser/dispatch tests for task trade guard arguments.

## 3. Implementation

- [x] 3.1 Add lifecycle owner-lock guard parameters to `TdxTaskManager.trade_buy`, `trade_sell`, and `trade_submit_once`.
- [x] 3.2 Forward task CLI guard arguments through `task trade-buy`, `task trade-sell`, and `task trade-submit-once`.
- [x] 3.3 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## 4. Verification

- [x] 4.1 Run focused pytest for API task/CLI and FUNCTION_TREE registry.
- [x] 4.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 4.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
