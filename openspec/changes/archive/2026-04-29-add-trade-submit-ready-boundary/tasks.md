## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for stable trade submit-ready manager behavior and nested trade submit-ready CLI parsing/dispatch.

## 2. Submit-Ready Implementation

- [x] 2.1 Implement a stable `TdxTradeManager.pingan.submit_ready(...)` workflow that reuses the HID submit probe path, validates confirm visibility, and stops before confirm click.
- [x] 2.2 Extend trade safety metadata helpers so submit-ready can report `local_state_mutating` without affecting existing live trade workflows.
- [x] 2.3 Add nested `trade submit-ready` CLI parsing and dispatch.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show the stable submit-ready boundary entrypoint and narrow the remaining confirmation-gap narrative.
- [x] 3.2 Run focused pytest, full `tests/` pytest, compile, and OpenSpec validation, then archive the change if complete.
