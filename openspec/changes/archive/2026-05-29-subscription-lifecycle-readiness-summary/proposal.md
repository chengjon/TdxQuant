## Why

Subscription long-run governance now exposes separate read-only signals for statefile ownership, restart preflight, and supervisor daemon state. Operators still need one stable readiness summary that says whether the current evidence is sufficient for manual lifecycle control without reading several nested objects.

## What Changes

- Add a read-only `status_summary.lifecycle_readiness` object to subscription-watch background status.
- Derive readiness only from existing in-memory/detailed status evidence: `statefile_ownership`, `restart_preflight`, and `supervisor_daemon`.
- Preserve the same object through CLI and HTTP `watch-status --view summary`.
- Keep the boundary explicit: this is a readiness/status projection only and MUST NOT execute start/stop/restart/supervise/backoff/probe behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: add a stable read-only lifecycle readiness projection to the existing subscription long-run status summary contract.

## Impact

- Code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`.
- Tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`.
- Registry: `FUNCTION_TREE.md` B-16/E-09 remains `[部分实现]` with explicit evidence and boundary.
