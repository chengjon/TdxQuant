## Why

The subscription long-run summary views already expose status and advisory governance rollups, but operators still need a compact way to correlate the summary with the active controller/run identity. Today that identity remains only in the detailed `control` and `watch_status` payloads, which pushes summary consumers back to the detailed view for routine triage.

## What Changes

- Add a read-only runtime identity projection to bridge watch-status summary views.
- Include selected fields derived from existing detailed payloads: control state/activity, watch state, run id, and pid when present.
- Keep raw `control` and `watch_status` out of the compact summary view.
- Preserve existing detailed payload defaults and all reconnect/backoff/lifecycle behavior.
- Update B-16/E-09 in `FUNCTION_TREE.md` with explicit evidence and boundaries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`: CLI summary view includes selected runtime identity fields as a read-only projection.
- `tdx-worker-bridge-http-control-plane`: HTTP summary view includes the same selected runtime identity fields as a read-only projection.

## Impact

- Bridge watch-status CLI summary helper in `tdxquant/cli.py`.
- Worker bridge HTTP watch-status summary helper in `tdxquant/bridge_http.py`.
- CLI and HTTP summary tests in `tests/test_api_cli.py` and `tests/test_bridge_http.py`.
- `FUNCTION_TREE.md` B-16/E-09 evidence and boundary text.
