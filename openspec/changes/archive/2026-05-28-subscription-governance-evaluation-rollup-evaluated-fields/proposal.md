# Change: Add evaluated-component fields to subscription evaluation rollup

## Why

HTTP and CLI watch-status summary views already expose `governance.evaluation_rollup` so callers can inspect compact governance staleness metadata without expanding raw control/watch payloads or full advisory arrays. The rollup includes stale, fresh, and not-evaluated primary components, but it omits the matching evaluated-component hint even though detailed `governance.evaluation_summary.primary_evaluated_component` already exists.

Adding evaluated-component fields keeps the compact rollup symmetrical and lets dashboards answer whether any component was evaluated without reading the larger detailed summary.

## What Changes

- Add `primary_evaluated_component` to HTTP and CLI summary-view `governance.evaluation_rollup`.
- Add `has_evaluated_component` to HTTP and CLI summary-view `governance.evaluation_rollup`.
- Update tests and FUNCTION_TREE evidence while keeping B-16/E-09 `[部分实现]`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`

