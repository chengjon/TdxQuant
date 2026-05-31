## 1. Tests

- [x] 1.1 Add a trade manager regression proving required owner-lock failure rejects before submit-ready HID submit probe or confirm lookup.
- [x] 1.2 Add task manager coverage proving `trade_submit_ready` forwards lifecycle owner-lock guard options while default dispatch stays unchanged.
- [x] 1.3 Add CLI parser/dispatch coverage for `trade submit-ready` and `task trade-submit-ready` owner-lock guard options.
- [x] 1.4 Add FUNCTION_TREE registry coverage proving D-07 remains `[部分实现]` with explicit submit-ready guard evidence and boundaries.

## 2. Implementation

- [x] 2.1 Add optional lifecycle owner-lock guard parameters to `TdxTradeManager.pingan.submit_ready(...)`.
- [x] 2.2 Forward lifecycle owner-lock guard options through `TdxTaskManager.trade_submit_ready(...)`.
- [x] 2.3 Expose and dispatch lifecycle owner-lock guard options for stable submit-ready CLI/task commands.
- [x] 2.4 Update `FUNCTION_TREE.md` D-07 evidence and boundary without claiming D-07 is implemented.

## 3. Verification

- [x] 3.1 Run focused pytest for trade manager, task manager, CLI, and FUNCTION_TREE registry coverage.
- [x] 3.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
