## 1. Tests

- [x] 1.1 Add a trade manager regression proving required broker readiness failure rejects before confirm dialog lookup/click.
- [x] 1.2 Add task manager coverage proving `trade_confirm_current` forwards `require_broker_readiness`.
- [x] 1.3 Add CLI parser/dispatch coverage for `trade confirm-current` and `task trade-confirm-current` broker readiness guard options.
- [x] 1.4 Add FUNCTION_TREE registry coverage proving D-07 remains `[部分实现]` with explicit broker readiness guard evidence and boundaries.

## 2. Implementation

- [x] 2.1 Add broker readiness guard evaluation to `TdxTradeManager.pingan.confirm_current(...)`.
- [x] 2.2 Forward `require_broker_readiness` through `TdxTaskManager.trade_confirm_current(...)`.
- [x] 2.3 Expose and dispatch `--require-broker-readiness` for stable confirm-current CLI/task commands.
- [x] 2.4 Update `FUNCTION_TREE.md` D-07 evidence and boundary without claiming D-07 is implemented.

## 3. Verification

- [x] 3.1 Run focused pytest for trade manager, task manager, CLI, and FUNCTION_TREE registry coverage.
- [x] 3.2 Run `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
- [x] 3.3 Archive the OpenSpec change, repeat verification, and commit only this slice.
