# Change: Add control rollup to subscription status summary

## Why

Subscription background status already reconciles control state from the active statefile and owned PID file, but compact status consumers do not get a stable read-only summary of control identity and terminal reason signals. Callers must inspect raw `control` payloads to distinguish an active control record from a stopped or stale-process control record.

Adding `status_summary.control_rollup` makes statefile-derived control identity visible without exposing raw payloads or claiming process ownership, readiness, restart, backoff, or lifecycle control.

## What Changes

- Add core `status_summary.control_rollup` derived from the existing reconciled `control` payload.
- Project `status_summary.control_rollup` through HTTP `watch/status?view=summary`.
- Project `status_summary.control_rollup` through CLI `bridge watch-status --view summary`.
- Update focused tests and FUNCTION_TREE B-16/E-09 evidence while keeping both nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
