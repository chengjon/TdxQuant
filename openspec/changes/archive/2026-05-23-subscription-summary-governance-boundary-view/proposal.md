## Why

Detailed subscription watch status already includes `status_summary.governance.boundary`, which states that governance output is advisory-only and does not trigger reconnect, backoff, restart, or lifecycle changes.

The compact HTTP/CLI summary views project governance decision, action rollup, and evaluation rollup, but they omit the boundary marker. That makes the compact view less self-describing than the detailed payload and leaves room for readers to over-interpret governance fields as active automation.

## What Changes

- Add `governance.boundary` to bridge HTTP `watch/status?view=summary` when the underlying status summary provides it.
- Add `governance.boundary` to CLI `bridge watch-status --view summary` under the same condition.
- Preserve existing reduced-view behavior: no full `governance.actions`, no raw `control`/`watch_status`, and no lifecycle/reconnect side effects.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: compact subscription summary views expose the advisory governance boundary marker.

## Impact

- Code: `tdxquant/bridge_http.py`, `tdxquant/cli.py`
- Tests: `tests/test_bridge_http.py`, `tests/test_api_cli.py`
- Docs/registry: `FUNCTION_TREE.md`
