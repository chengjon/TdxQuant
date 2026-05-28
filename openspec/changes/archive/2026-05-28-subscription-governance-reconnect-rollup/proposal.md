# Change: Add reconnect rollup to subscription governance summary

## Why

Subscription long-run status already includes reconnect diagnostics, but the governance section does not provide a compact reconnect/backoff-oriented rollup. Callers must inspect the full `status_summary.reconnect` object to understand whether reconnect state was evaluated, whether failures exist, whether a next reconnect timestamp is present, or whether a last error was observed.

Adding a read-only `governance.reconnect_rollup` creates a stable summary for dashboards and validators without executing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

## What Changes

- Add core `governance.reconnect_rollup` to `build_subscription_watch_status_summary()`.
- Project `governance.reconnect_rollup` through HTTP `watch/status?view=summary`.
- Project `governance.reconnect_rollup` through CLI `bridge watch-status --view summary`.
- Update focused tests and FUNCTION_TREE B-16/E-09 evidence while keeping both nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
