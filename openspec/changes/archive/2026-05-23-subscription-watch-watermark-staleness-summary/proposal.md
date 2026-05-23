## Why

B-16/E-09 already expose a long-run status summary and optional heartbeat staleness evaluation. The watermark section still only reports raw event counters and timestamps, so operators cannot ask the same read-only question for event flow freshness: "has the last event watermark gone stale?"

This change adds explicit watermark staleness evaluation while preserving the current default behavior and avoiding any reconnect/backoff side effect.

## What Changes

- Add `watermark_stale_after_seconds` to `build_subscription_watch_status_summary()` and `SubscriptionWatchBackgroundController.status()`.
- Evaluate `watermark.staleness`, `age_seconds`, `stale_after_seconds`, and `evaluated_at` when a caller provides a positive threshold and `last_event_ts` is parseable.
- Forward the threshold through bridge HTTP, worker registry, and `bridge watch-status`.
- Update `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: status summary supports explicit watermark staleness diagnostics.
- `tdx-data-api-bridge`: bridge watch-status forwards the watermark stale threshold.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_bridge_registry.py`, `tests/test_api_cli.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
