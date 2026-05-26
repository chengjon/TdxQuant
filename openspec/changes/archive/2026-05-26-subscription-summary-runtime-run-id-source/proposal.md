# Add subscription summary runtime run-id source

## Why

Subscription watch summary views already project a compact `runtime.run_id` derived from `watch_status.run_id` with a fallback to `control.run_id`. That keeps the summary compact, but consumers cannot tell which source supplied the displayed run id.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. A read-only `runtime.run_id_source` improves runtime identity diagnostics without changing lifecycle behavior.

## What Changes

- Add read-only `runtime.run_id_source` to HTTP and CLI `watch-status --view summary` payloads when `runtime.run_id` is projected.
- Report `watch_status` when `watch_status.run_id` is present.
- Report `control` when `watch_status.run_id` is absent and `control.run_id` supplies the value.
- Do not alter reconnect, backoff, restart, lifecycle, SSE, event-stream, or controller behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/bridge_http.py` and `tdxquant/cli.py` runtime summary projection helpers.
- Adds focused HTTP and CLI summary-view assertions.
- Updates `FUNCTION_TREE.md` B-16/E-09 with explicit status, evidence, and boundary.
