## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for stable trade health manager behavior and nested trade health CLI parsing/dispatch.

## 2. Trade Health Implementation

- [x] 2.1 Implement a read-only `TdxTradeManager.pingan.health(...)` workflow with broker/runtime summary, artifact targets, and optional HID ping.
- [x] 2.2 Add nested `trade health` CLI parsing and dispatch.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show the stable trade health entrypoint and clarified remaining trade-governance gaps.
- [x] 3.2 Run focused pytest, compile, and OpenSpec validation, then archive the change if complete.
