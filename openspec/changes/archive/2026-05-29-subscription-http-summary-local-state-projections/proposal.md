## Why

CLI `bridge watch-status --view summary` now preserves local state projections under `status_summary`, but HTTP `GET /bridge/v1/watch/status?view=summary` still uses its own summary builder and does not preserve the same `status_summary.statefile_ownership` / `status_summary.supervisor_daemon` fields. This creates an avoidable mismatch between the two supported summary surfaces for B-16/E-09 long-run governance observability.

## What Changes

- Preserve `status_summary.statefile_ownership` in HTTP watch-status summary view.
- Preserve `status_summary.supervisor_daemon` in HTTP watch-status summary view.
- Keep the existing top-level HTTP summary `supervisor_daemon` projection unchanged for compatibility.
- Do not change detailed status, diagnostics view, lifecycle control, restart/backoff, probes, or event streaming.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: align HTTP summary view with the existing `status_summary` local-state projections.

## Impact

- Affected code: `tdxquant/bridge_http.py`.
- Affected tests: `tests/test_bridge_http.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No new dependency, provider mutation, daemon lifecycle default, scheduler, or trading behavior.
