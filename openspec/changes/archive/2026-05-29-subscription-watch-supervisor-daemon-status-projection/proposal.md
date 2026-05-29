## Why

Operators now have explicit supervisor daemon start/status/stop controls, but the normal watch-status views do not show whether a daemon statefile, pidfile, owner marker, or process liveness is present. B-16/E-09 needs this read-only projection before any larger daemon policy work, so operators can inspect daemon state without executing lifecycle actions.

## What Changes

- Add the existing supervisor daemon status payload to the worker-local background `status()` result as a read-only diagnostic field.
- Project a compact supervisor daemon summary in bridge `watch-status --view summary`.
- Project the same compact supervisor daemon diagnostic in bridge `watch-status --view diagnostics`.
- Keep raw owner token and full daemon settings out of summary/diagnostics projections.
- Do not start, stop, restart, supervise, back off, or schedule any process from watch-status.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-task-subscription-watch-background-control`: include read-only supervisor daemon status in background watch status.
- `tdx-worker-bridge-http-control-plane`: include compact supervisor daemon status in HTTP summary and diagnostics projections.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/subscription_watch_status_diagnostics.py`.
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No new CLI command, registry helper, task/report/trade/workflow/catalog behavior, or daemon policy.
