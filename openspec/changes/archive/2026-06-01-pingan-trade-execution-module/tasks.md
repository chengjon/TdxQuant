## 1. Contract and Red Tests

- [x] 1.1 Validate OpenSpec artifacts before implementation.
- [x] 1.2 Add focused red tests for the internal PingAn execution request/seam.
- [x] 1.3 Add compatibility tests that `buy_submit_once` preserves existing dispatch/audit/gate behavior when delegated.

## 2. Implementation

- [x] 2.1 Create `tdxquant.trade.pingan_execution` with normalized request and execution result helpers.
- [x] 2.2 Delegate `TdxTradeManager.pingan.buy_submit_once(...)` through the new module without changing public behavior.
- [x] 2.3 Keep existing sell/buy/confirm-current paths unchanged except for shared helper reuse if required by the tracer bullet.

## 3. Registry and Verification

- [x] 3.1 Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary for the internal execution seam.
- [x] 3.2 Run focused pytest, OpenSpec strict validation, diff whitespace check, and FUNCTION_TREE registry validation.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
