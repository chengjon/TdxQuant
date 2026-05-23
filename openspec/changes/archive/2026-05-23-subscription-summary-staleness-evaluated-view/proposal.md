# Add Staleness Evaluated Flag To Subscription Summary View

## Why

B-16 and E-09 now expose read-only governance action rollups in subscription long-run summary views. The detailed `status_summary.governance` payload already includes `staleness_evaluated`, but the reduced HTTP/CLI summary view omits it, so callers cannot tell whether the summary view reflects explicit stale-threshold evaluation or the default observe-only path.

## What Changes

- Include `governance.staleness_evaluated` in bridge HTTP `watch/status?view=summary`.
- Include `governance.staleness_evaluated` in CLI `bridge watch-status --view summary`.
- Keep the field read-only and derived from existing `status_summary.governance`.
- Update B-16/E-09 evidence and boundary in `FUNCTION_TREE.md`.

## Impact

- Affected spec: `tdx-subscription-long-run-status-summary`
- Affected code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Boundary: no reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior changes.
