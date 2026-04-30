## 1. OpenSpec And Tests

- [x] 1.1 Add RED tests for task manager split-step workflows, task CLI subcommands, and preset-driven execution.

## 2. Task Split-Step Workflow Implementation

- [x] 2.1 Add `trade_submit_ready(...)` and `trade_confirm_current(...)` to `TdxTaskManager` as thin wrappers over the stable trade manager workflows.
- [x] 2.2 Extend task CLI parsing, preset resolution, and dispatch to support `task trade-submit-ready`, `task trade-confirm-current`, and `task run --preset ...` for both commands.
- [x] 2.3 Add default task profile mappings and preset-ready defaults for the new split-step trade task commands.

## 3. Documentation And Verification

- [x] 3.1 Update docs to show that split-step desktop trading is now available through stable task workflows.
- [x] 3.2 Run focused pytest, full `tests/`, compile, and OpenSpec validation; archive the change if complete.
