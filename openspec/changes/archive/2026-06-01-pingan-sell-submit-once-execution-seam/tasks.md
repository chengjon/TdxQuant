## 1. Contract and Red Tests

- [x] 1.1 Validate OpenSpec artifacts before implementation.
- [x] 1.2 Add a red manager routing test for `sell_submit_once` delegating through `execute_pingan_order`.

## 2. Implementation

- [x] 2.1 Delegate `TdxTradeManager.pingan.sell_submit_once(...)` through `PingAnExecutionRequest` and `execute_pingan_order`.
- [x] 2.2 Preserve existing sell submit-once method identity, risk/idempotency gates, and `run_pingan_sell_fast` desktop dispatch boundary.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-08 incremental evidence and boundary.
- [x] 3.2 Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
