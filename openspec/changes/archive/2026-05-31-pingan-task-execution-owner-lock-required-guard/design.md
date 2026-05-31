## Context

The PingAn manager execution methods already accept `lifecycle_statefile_path`, `lifecycle_owner_token`, `lifecycle_stale_after_seconds`, and `require_lifecycle_owner_lock`. The nested stable trade CLI and `PingAnDesktopTraderGateway` can forward those options, but the task layer currently exposes the same side-effecting trade operations without those arguments.

## Approach

- Reuse the existing owner-lock guard contract in `TdxTradeManager.pingan.*`; do not add a second guard implementation.
- Add the four optional guard parameters to `TdxTaskManager.trade_buy`, `trade_sell`, and `trade_submit_once`.
- Reuse the existing CLI helper for lifecycle owner-lock guard arguments on `task trade-buy`, `task trade-sell`, and `task trade-submit-once`.
- Forward parsed task CLI values through `_run_trade_buy`, `_run_trade_sell`, and `_run_trade_submit_once`.
- Keep presets unchanged unless a future slice needs preset defaults; CLI callers can opt in with explicit arguments.

## Boundaries

- The task guard is opt-in and local to the existing statefile owner-lock evidence.
- The task layer does not acquire/release owner locks and does not write lifecycle statefile/lock artifacts directly.
- The task layer does not start, stop, restart, kill, supervise, or back off PingAn processes.
- Passing the guard only allows the existing trade path to continue; it does not prove broker readiness, production readiness, or live/manual acceptance.
- D-07 and D-08 remain `[部分实现]`.

## Verification

- Red tests first for parser/dispatch and task manager forwarding.
- Focused pytest for API task/CLI/FUNCTION_TREE registry.
- `openspec validate --all --strict`, `git diff --check`, and `python scripts/validate_function_tree_registry.py`.
