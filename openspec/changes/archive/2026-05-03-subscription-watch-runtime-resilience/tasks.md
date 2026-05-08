## 1. Run artifact resilience fields

- [x] 1.1 Extend `tdxquant/subscription_watch_run.py` status/summary builders with reconnect/degraded fields
- [x] 1.2 Lock the resilience field contract in `tests/test_subscription_watch_run.py`

## 2. Foreground reconnect and degraded recovery

- [x] 2.1 Add bounded reconnect and degraded low-frequency recovery to `TdxTaskManager.subscription_watch(...)`
- [x] 2.2 Preserve single-run identity and keep `events.jsonl` free of synthetic reconnect lifecycle events
- [x] 2.3 Lock reconnect recovery and degraded behavior with focused `tests/test_api_manager.py` coverage

## 3. Background reconcile and terminal cleanup

- [x] 3.1 Treat `reconnecting / degraded` as active-process states in `subscription_watch_background.py`
- [x] 3.2 Normalize stale resilience states to `failed(stale_process_state)` and keep `stopping` -> `stopped`
- [x] 3.3 Clear `next_reconnect_at` on terminal status persistence in `subscription_watch_background_runner.py`
- [x] 3.4 Lock background/runner/bridge resilience behavior with focused tests

## 4. Fixtures, docs, and verification

- [x] 4.1 Add representative resilience replay fixtures and register them in `tdxquant/replay_fixtures.py`
- [x] 4.2 Keep completed subscription-watch fixtures compatible while extending them with optional resilience fields
- [x] 4.3 Update subscription-watch contract and roadmap docs for reconnect/degraded runtime resilience
- [x] 4.4 Run resilience-focused regression and `git diff --check`
