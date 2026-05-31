## Context

`TdxTaskManager.trade_buy`, `trade_sell`, and `trade_submit_once` already accept lifecycle owner-lock guard options, and direct task commands now parse and forward those options. `task run` resolves a preset into a task command namespace, merges preset options with CLI overrides, and then dispatches through the same task command handler.

The remaining gap is the run parser: without explicit `task run` guard flags, operators cannot override preset owner-lock guard values at invocation time. The merge helper also needs to treat the stale timeout as optional so a preset value is not shadowed by a parser default.

## Approach

- Add lifecycle owner-lock guard arguments to `_add_task_run_arguments`.
- Use `default=None` for the `task run` stale timeout so preset options can supply a value.
- Make `_get_lifecycle_owner_guard_kwargs` treat missing or `None` stale timeout as `300.0`.
- Add tests for CLI override precedence and preset-provided guard options.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary without changing status.

## Boundaries

- This change only controls argument parsing, preset merge behavior, and forwarding.
- It does not add or modify task presets.
- It does not execute catalog bundles or add a workflow builder.
- It does not acquire/release lifecycle owner locks or write lifecycle statefile/lock artifacts.
- It does not start, stop, restart, kill, supervise, or back off PingAn processes.
- D-07 and D-08 remain `[部分实现]`.

## Verification

- Red tests first for `task run` parser/dispatch gaps.
- Focused pytest for API CLI and FUNCTION_TREE registry.
- `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
