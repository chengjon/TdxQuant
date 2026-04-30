## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for stable trade confirm-current manager behavior and nested trade confirm-current CLI parsing/dispatch.

## 2. Confirm-Current Implementation

- [x] 2.1 Implement a stable `TdxTradeManager.pingan.confirm_current(...)` workflow that advances the current confirm dialog, summarizes the result dialog, and optionally closes it.
- [x] 2.2 Add nested `trade confirm-current` CLI parsing and dispatch.
- [x] 2.3 Preserve state/event artifact persistence while excluding submission-ledger behavior for confirm-current.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show the stable `submit-ready` + `confirm-current` split-step pair and narrow the remaining trade-governance narrative.
- [x] 3.2 Run focused pytest, full `tests/` pytest, compile, and OpenSpec validation, then archive the change if complete.
