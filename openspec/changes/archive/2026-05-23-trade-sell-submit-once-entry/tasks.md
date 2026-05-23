## 1. Sell Submit-Once Identity Tests

- [x] 1.1 Add trade manager coverage proving `sell_submit_once` uses the sell desktop flow while recording `sell_submit_once` metadata.
- [x] 1.2 Add gateway coverage proving submit-once sell orders call `pingan.sell_submit_once`.
- [x] 1.3 Add task manager coverage proving `side=sell` submit-once routes through `pingan.sell_submit_once`.

## 2. Sell Submit-Once Identity Implementation

- [x] 2.1 Add `TdxTradeManager.pingan.sell_submit_once` with existing safety/idempotency handling and sell desktop execution.
- [x] 2.2 Route submit-once sell gateway/task calls through the dedicated manager method without changing CLI arguments.

## 3. Registry And Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 evidence and boundary without claiming a new desktop primitive or broader broker coverage.
- [x] 3.2 Run focused tests, OpenSpec validation, diff checks, and the FUNCTION_TREE validator.
