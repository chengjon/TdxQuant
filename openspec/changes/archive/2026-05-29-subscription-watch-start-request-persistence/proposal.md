# Change: Persist subscription-watch start request metadata

## Why

B-16/E-09 already has worker-local `subscription-watch` start/stop/status control and extensive read-only governance diagnostics. The next real lifecycle prerequisite is durable start intent: a future restart/backoff controller cannot safely recreate a worker run unless the original `stock_list`, `max_events`, `max_seconds`, and `poll_interval` request are recorded with the active run state.

Currently `active.json` records ownership metadata such as `run_id`, `pid`, `state`, `reason`, `runner_log_path`, and `idempotency_key`, but it does not persist the normalized start request. That keeps restart/backoff work blocked or forces it to infer intent from process arguments/logs, which is a weaker ownership model.

## What Changes

- Add a `start_request` object to newly written subscription-watch active state.
- Store normalized `stock_list`, `max_events`, `max_seconds`, and `poll_interval` values used to spawn the runner.
- Preserve this metadata through status reads and same-idempotency replay responses.
- Keep existing start/stop semantics unchanged.

## Impact

- Specs: `tdx-task-subscription-watch-background-control`.
- Code: `tdxquant/subscription_watch_background.py`.
- Tests: `tests/test_subscription_watch_background.py`.
- FUNCTION_TREE: update B-16/E-09 as `[部分实现]` with evidence and boundary.

