# Change: Add explicit subscription-watch restart control

## Why

B-16/E-09 now records the normalized `subscription-watch` start request in active state. That makes a safe explicit restart operation possible without inferring operator intent from process arguments or logs.

Operators need a single restart control path that stops the currently owned background run and starts a replacement with the persisted start request. This is a concrete step toward long-run lifecycle governance while staying narrower than automatic backoff or supervisor behavior.

## What Changes

- Add `SubscriptionWatchBackgroundController.restart()`.
- Restart uses the active run's persisted `start_request`.
- Restart returns a structured `stop_result`, `start_result`, `previous_run_id`, and `new_run_id`.
- Expose restart through worker bridge HTTP, registry client helper, and CLI.
- Keep restart explicit and operator-triggered only.

## Impact

- Specs: `tdx-task-subscription-watch-background-control`, `tdx-worker-bridge-http-control-plane`.
- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_bridge_registry.py`, `tests/test_api_cli.py`.
- FUNCTION_TREE: update B-16/E-09 evidence and boundary while keeping `[部分实现]`.
