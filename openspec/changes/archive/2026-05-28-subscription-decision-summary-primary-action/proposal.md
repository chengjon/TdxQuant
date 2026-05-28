# Change: Add primary action fields to subscription decision summary

## Why

HTTP and CLI watch-status summary views already expose `governance.decision_summary` for compact advisory status. It includes the governance decision, manual-review flag, reason/action counts, primary reason source, severity, and count presence flags, but callers still need to inspect `governance.action_summary` to see the first suggested action and its reason.

Adding primary action fields keeps the first-screen decision summary useful while preserving the existing read-only boundary.

## What Changes

- Add `primary_action` to HTTP and CLI summary-view `governance.decision_summary`.
- Add `primary_action_reason` to HTTP and CLI summary-view `governance.decision_summary`.
- Update tests and FUNCTION_TREE B-16/E-09 evidence while keeping the nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`

