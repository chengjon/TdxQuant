# Change: Add consistency rollup to subscription status summary

## Why

Subscription background status exposes reconciled `control` and optional `watch_status` payloads, while HTTP and CLI summary views separately project selected runtime identity fields. Direct `status_summary` callers do not yet get a stable compact object that reports whether control/watch states and run IDs are comparable and aligned.

Adding `status_summary.consistency_rollup` makes this read-only consistency signal available to direct status, HTTP summary, and CLI summary consumers without exposing raw payloads or claiming process ownership, PID liveness, readiness, restart, backoff, or lifecycle control.

## What Changes

- Add core `status_summary.consistency_rollup` derived from existing `control` and `watch_status` payloads.
- Project `status_summary.consistency_rollup` through HTTP `watch/status?view=summary`.
- Project `status_summary.consistency_rollup` through CLI `bridge watch-status --view summary`.
- Update focused tests and FUNCTION_TREE B-16/E-09 evidence while keeping both nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/subscription_watch_background.py`, `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_subscription_watch_background.py`, `tests/test_bridge_http.py`, `tests/test_api_cli.py`
