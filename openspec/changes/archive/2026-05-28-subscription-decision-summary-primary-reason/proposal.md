# Change: Add primary reason to subscription decision summary

## Why

HTTP and CLI watch-status summary views expose `governance.decision_summary.primary_reason_source`, but not the actual first governance reason. Callers must still inspect `governance.reason_summary` to see the reason that drove the compact advisory decision.

Adding `primary_reason` keeps the compact decision summary useful while preserving the existing read-only boundary.

## What Changes

- Add `primary_reason` to HTTP summary-view `governance.decision_summary`.
- Add `primary_reason` to CLI summary-view `governance.decision_summary`.
- Update tests and FUNCTION_TREE B-16/E-09 evidence while keeping the nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`

