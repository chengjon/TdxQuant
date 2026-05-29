## Why

Detailed subscription-watch status already includes `status_summary.boundary`, but CLI and HTTP summary views omit that boundary even while projecting the rest of `status_summary`. This weakens the single-read summary contract because consumers cannot see that the summary is projection-only and does not change reconnect/backoff behavior.

## What Changes

- Preserve `status_summary.boundary` in CLI `bridge watch-status --view summary`.
- Preserve `status_summary.boundary` in HTTP `GET /bridge/v1/watch/status?view=summary`.
- Do not change detailed status, diagnostics view, governance evaluation, lifecycle control, restart/backoff, probes, or event streaming.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: expose the existing status summary boundary in summary views.

## Impact

- Affected code: `tdxquant/cli.py`, `tdxquant/bridge_http.py`.
- Affected tests: `tests/test_api_cli.py`, `tests/test_bridge_http.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No new runtime dependency, provider mutation, scheduler, daemon lifecycle default, or trading behavior.
