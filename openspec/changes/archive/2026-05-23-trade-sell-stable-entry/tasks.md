## 1. Sell Entry Tests

- [x] 1.1 Add parser and dispatch tests for stable `trade sell` and `task trade-sell`.
- [x] 1.2 Add task manager tests for sell success and refresh abort behavior.

## 2. Sell Entry Implementation

- [x] 2.1 Implement stable `trade sell` CLI dispatch through the trade service path.
- [x] 2.2 Implement `TdxTaskManager.trade_sell` and task CLI dispatch through the existing Ping An sell manager path.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-07 evidence and boundary without overclaiming broker coverage.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
