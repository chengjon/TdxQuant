## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for stable trade preflight manager behavior and nested trade preflight CLI parsing/dispatch.

## 2. Trade Preflight Implementation

- [x] 2.1 Implement a read-only `TdxTradeManager.pingan.preflight(...)` workflow with broker/runtime, buy-page detection, risk gate, idempotency, and HID ping checks.
- [x] 2.2 Add nested `trade preflight` CLI parsing and dispatch.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show the stable trade preflight entrypoint and narrowed remaining trade-governance gaps.
- [x] 3.2 Run focused pytest, compile, and OpenSpec validation, then archive the change if complete.
