# Add Bridge Watch Status HTTP Summary View

## Why

`bridge watch-status --view summary` gives operators a compact, read-only view of
subscription long-run status and governance action rollups. Remote bridge callers
still receive only the detailed `GET /bridge/v1/watch/status` envelope, so they
must duplicate the CLI projection when they only need the same summary.

## What Changes

- Add an opt-in `view=summary` query parameter to `GET /bridge/v1/watch/status`.
- Keep the default HTTP response as the current detailed controller status.
- Reuse the same compact fields as the CLI summary view: worker, status,
  selected `status_summary` fields, and advisory governance rollup.
- Keep stale-threshold query forwarding unchanged.
- Update tests and `FUNCTION_TREE.md` so B-16/E-09 clearly remain read-only
  status projection work.

## Out of Scope

- Reconnect, backoff, restart, or daemon lifecycle changes.
- SSE/event-stream behavior changes.
- Changing `watch/start`, `watch/stop`, `watch/list`, `watch/events`,
  `watch/artifacts`, or `watch/logs`.
- Making summary view the default response.

## Impact

- Affected spec: `tdx-worker-bridge-http-control-plane`
- Affected code: `tdxquant/bridge_http.py`
- Affected tests: `tests/test_bridge_http.py`
