## Why

The subscription long-run governance payload exposes `staleness_evaluated` and advisory actions, but callers still need to inspect each heartbeat/watermark/reconnect sub-object to see which components were evaluated and which were stale. A compact evaluation rollup keeps summary views useful without exposing full governance actions or changing lifecycle behavior.

## What Changes

- Add a read-only `governance.evaluation_summary` object to subscription long-run status summaries.
- Include evaluated, stale, and not-evaluated component lists for heartbeat, watermark, and reconnect.
- Project `evaluation_summary` through CLI and HTTP watch-status summary views.
- Preserve detailed payload defaults and keep governance advisory-only.
- Update B-16/E-09 in `FUNCTION_TREE.md` with the new evidence and boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: governance status includes a compact staleness evaluation rollup.
- `tdx-worker-bridge-http-control-plane`: HTTP summary view includes the governance evaluation rollup when present.

## Impact

- Subscription watch background summary builder in `tdxquant/subscription_watch_background.py`.
- CLI and HTTP watch-status summary projection helpers in `tdxquant/cli.py` and `tdxquant/bridge_http.py`.
- Tests in `tests/test_subscription_watch_background.py`, `tests/test_api_cli.py`, and `tests/test_bridge_http.py`.
- `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.
