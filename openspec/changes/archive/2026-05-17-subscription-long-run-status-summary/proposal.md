## Why

Subscription foreground runs and background bridge control already persist status payloads with reconnect, degraded, heartbeat, and event watermark fields. The remaining long-run wrapper gap is that callers must inspect raw nested status data themselves instead of receiving a stable status summary that separates health, heartbeat, watermark, and reconnect metadata.

## What Changes

- Add a stable `status_summary` projection for subscription-watch background status responses.
- Summarize controller state, active run identity, heartbeat presence, event watermark fields, and reconnect/degraded metadata.
- Preserve raw `control` and `watch_status` payloads for compatibility.
- Update `FUNCTION_TREE.md` so E-09 is partially implemented with explicit remaining long-run governance boundaries.

## Capabilities

### New Capabilities
- `tdx-subscription-long-run-status-summary`: Covers stable status summary projection for long-running subscription-watch state, heartbeat, watermark, and reconnect metadata.

### Modified Capabilities
- `tdx-task-subscription-watch-background-control`: Adds `status_summary` to background watch status responses without changing start/stop/list/event/log semantics.

## Impact

- Affected code: `tdxquant/subscription_watch_background.py` and focused background controller tests.
- Affected docs/specs: OpenSpec specs and `FUNCTION_TREE.md`.
- No reconnect scheduler rewrite, no backoff algorithm changes, no event stream contract change, and no worker process-management changes.
