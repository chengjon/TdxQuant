## Context

The task trade layer already supports lifecycle owner-lock guard forwarding for direct `trade-buy`, `trade-sell`, and `trade-submit-once` workflows. `guarded_trade_buy` runs additional snapshot/block/formula prechecks and then calls `self.trade_buy(...)`; it should forward the same opt-in guard options to that delegated trade execution.

## Approach

- Reuse `_build_task_lifecycle_owner_lock_guard_kwargs` in `guarded_trade_buy`.
- Add optional guard parameters to the method signature and include them in guarded input/report payloads only when explicitly provided or enabled.
- Reuse `_add_trade_lifecycle_owner_guard_arguments` for `task guarded-trade-buy`.
- Pass `_get_lifecycle_owner_guard_kwargs(args)` through guarded CLI dispatch.
- Update only D-07 registry evidence because guarded buy belongs to buy-side workflow evidence, not submit-once.

## Boundaries

- Guarded workflow still delegates enforcement to `trade_buy` and the underlying PingAn manager execution guard.
- The guarded workflow does not acquire/release owner locks.
- The guarded workflow does not write lifecycle statefile/lock artifacts directly.
- The guarded workflow does not start, stop, restart, kill, supervise, or back off PingAn processes.
- D-07 remains `[部分实现]`.

## Verification

- Red tests first for guarded task manager and CLI forwarding gaps.
- Focused pytest for guarded task/CLI and FUNCTION_TREE registry.
- `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
