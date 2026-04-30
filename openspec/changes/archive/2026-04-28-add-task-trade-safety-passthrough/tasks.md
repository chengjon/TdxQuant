## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for task parser, dispatch, and task-manager passthrough of `submission_key` and `max_price`.

## 2. Task Safety Passthrough Implementation

- [x] 2.1 Extend stable trade-oriented task manager methods to accept and forward `submission_key` and `max_price`.
- [x] 2.2 Extend task CLI parsing, preset-run arguments, and subcommand dispatch to preserve the same safety controls.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show that task-layer trade workflows now expose the stable trade safety controls.
- [x] 3.2 Run focused pytest, compile, and OpenSpec validation, then archive the change if complete.
