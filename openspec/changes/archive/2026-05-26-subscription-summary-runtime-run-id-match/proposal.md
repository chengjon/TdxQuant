# Add subscription summary runtime run-id match

## Why

Subscription watch summary views now expose compact runtime identity fields, including `runtime.run_id`, `runtime.run_id_source`, `runtime.control_state`, and `runtime.watch_state`. Consumers can see which source supplied the displayed run id, but they still have to inspect the detailed payload to know whether `control.run_id` and `watch_status.run_id` agree when both are present.

B-16 and E-09 remain partial long-run governance work in `FUNCTION_TREE.md`. A read-only `runtime.run_id_match` hint improves identity diagnostics without changing lifecycle behavior.

## What Changes

- Add read-only `runtime.run_id_match` to HTTP and CLI `watch-status --view summary` payloads when both `control.run_id` and `watch_status.run_id` are present.
- Derive the field as `control.run_id == watch_status.run_id`.
- Omit the field when either run id source is missing.
- Do not alter reconnect, backoff, restart, lifecycle, SSE, event-stream, or controller behavior.

## Capabilities

### Modified Capabilities

- `tdx-subscription-long-run-status-summary`

## Impact

- Touches `tdxquant/bridge_http.py` and `tdxquant/cli.py` runtime summary projection helpers.
- Adds focused HTTP and CLI summary-view assertions.
- Updates `FUNCTION_TREE.md` B-16/E-09 with explicit status, evidence, and boundary.
