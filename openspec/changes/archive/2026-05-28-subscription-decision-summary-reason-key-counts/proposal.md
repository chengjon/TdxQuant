# Change: Add reason key counts to subscription decision summary

## Why

HTTP and CLI watch-status summary views expose compact `governance.decision_summary` fields for the advisory decision, but callers still need to inspect `governance.reason_summary` to understand how many distinct reason sources and reason codes contributed to the decision.

Adding read-only key counts keeps the compact decision summary useful for dashboards and validators without exposing raw reason payloads or changing subscription governance behavior.

## What Changes

- Add `reason_source_key_count` to HTTP summary-view `governance.decision_summary`.
- Add `reason_code_key_count` to HTTP summary-view `governance.decision_summary`.
- Add the same fields to CLI summary-view `governance.decision_summary`.
- Update tests and FUNCTION_TREE B-16/E-09 evidence while keeping the nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
