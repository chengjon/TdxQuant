## Why

`B-16` and `E-09` already expose heartbeat and watermark freshness as opt-in, read-only diagnostics, but reconnect/degraded duration is still only surfaced as raw reconnect metadata. Operators need the same explicit-threshold pattern for reconnect posture without implying automatic reconnect, backoff, restart, or daemon lifecycle behavior.

## What Changes

- Add an opt-in `reconnect_stale_after_seconds` threshold to subscription-watch status summary generation.
- Surface reconnect staleness in the existing `reconnect` sub-object and advisory governance reasons/actions.
- Pass the threshold through worker HTTP `GET /bridge/v1/watch/status`, bridge registry calls, and the bridge watch-status CLI.
- Keep default behavior unchanged: reconnect staleness remains `not_evaluated` unless explicitly requested.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: add explicit reconnect/degraded duration staleness evaluation to the read-only status summary.
- `tdx-worker-bridge-http-control-plane`: accept and forward the optional reconnect staleness query parameter for watch-status.

## Impact

- Affected code/tests: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`, `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_bridge_registry.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` nodes `B-16` and `E-09`
