# Change: Add primary action reason source to subscription decision summary

## Why

HTTP and CLI watch-status summary views now expose `governance.decision_summary.primary_action` and `primary_action_reason`, but callers still need to inspect `governance.action_summary` to know the parsed source of that action reason. The existing `decision_summary.primary_reason_source` is derived from `reason_summary`, so it does not necessarily describe the action reason.

Adding `primary_action_reason_source` makes the compact decision summary self-contained without exposing full advisory arrays or implying execution.

## What Changes

- Add `primary_action_reason_source` to HTTP summary-view `governance.decision_summary`.
- Add `primary_action_reason_source` to CLI summary-view `governance.decision_summary`.
- Update tests and FUNCTION_TREE B-16/E-09 evidence while keeping the nodes `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`

