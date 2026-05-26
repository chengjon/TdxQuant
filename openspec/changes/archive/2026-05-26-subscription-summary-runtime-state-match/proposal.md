# Add subscription summary runtime state match

## Why

Subscription watch summary views already project compact runtime identity fields from `control` and `watch_status`, including `control_state` and `watch_state`. Operators can compare those fields manually, but automation has to derive whether the controller and watch read models currently agree.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. A read-only `runtime.state_match` hint makes the summary view easier to scan without changing lifecycle behavior.

## What Changes

- Add read-only `runtime.state_match` to HTTP and CLI `watch-status --view summary` payloads when both `control.state` and `watch_status.state` are present.
- Derive `state_match` as `control.state == watch_status.state`.
- Omit `state_match` when either source state is missing.
- Do not alter reconnect, backoff, restart, lifecycle, SSE, event-stream, or controller behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/bridge_http.py` and `tdxquant/cli.py` runtime summary projection helpers.
- Adds focused HTTP and CLI summary-view assertions.
- Updates `FUNCTION_TREE.md` B-16/E-09 with explicit status, evidence, and boundary.
