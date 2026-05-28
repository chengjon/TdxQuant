# Change: Complete subscription governance evaluation rollup summary

## Why

`watch-status --view summary` and HTTP `watch/status?view=summary` already expose a compact `governance.evaluation_rollup`, but callers still need to inspect the larger `governance.evaluation_summary` object to answer two stable discovery questions:

- whether any governance component was not evaluated
- how many status categories are present in the component/evaluated status-count maps

These are read-only summary facts that help dashboards and catalog-style checks stay compact without implying reconnect, backoff, restart, lifecycle, SSE, or event-stream execution.

## What Changes

- Add `has_not_evaluated_component`, `component_status_key_count`, and `evaluated_status_key_count` to HTTP summary-view `governance.evaluation_rollup`.
- Add the same fields to CLI `bridge watch-status --view summary` `governance.evaluation_rollup`.
- Update tests and FUNCTION_TREE evidence for B-16/E-09.

## Impact

- Affected specs: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`

