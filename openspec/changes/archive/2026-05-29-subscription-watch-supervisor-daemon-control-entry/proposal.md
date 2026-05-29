## Why

The supervisor daemon lifecycle scaffold now exists in the worker-local background controller, but operators cannot reach it through the existing bridge control surfaces. B-16/E-09 needs explicit manual control entrypoints before any larger restart/backoff policy work can be evaluated safely.

## What Changes

- Add authenticated bridge HTTP routes for supervisor daemon status, explicit start, and explicit stop.
- Add bridge registry helpers for the same routes so master-side callers do not hard-code URLs.
- Add CLI subcommands that dispatch to the registry helpers and preserve the normal JSON output envelope.
- Keep the feature opt-in and manual: no default daemon autostart, no automatic restart/backoff policy, and no task/report/trade/workflow/catalog execution path.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-worker-bridge-http-control-plane`: expose explicit supervisor daemon status/start/stop control routes and registry helper dispatch.
- `tdx-api-cli-entry`: expose explicit bridge CLI subcommands for supervisor daemon status/start/stop.

## Impact

- Affected code: `tdxquant/bridge_http.py`, `tdxquant/bridge_registry.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_bridge_http.py`, `tests/test_bridge_registry.py`, `tests/test_api_cli.py`.
- Affected registry: `FUNCTION_TREE.md` B-16/E-09 evidence and boundary.
- No dependency or data format changes beyond the existing supervisor daemon state payload contract.
