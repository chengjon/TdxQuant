# Proposal: Subscription Summary Schema Version View

## Why

The detailed subscription watch status payload includes `status_summary.schema_version`, but the opt-in CLI/HTTP summary view currently omits it. Summary-view consumers can see selected heartbeat, watermark, reconnect, runtime, and governance fields, but cannot identify the status-summary schema without requesting the full raw payload.

## What Changes

Copy the existing detailed `status_summary.schema_version` into `watch-status --view summary` and `watch/status?view=summary` responses when the detailed summary provides it.

## Out Of Scope

- No schema version changes.
- No raw `control`, `watch_status`, full `governance.reasons`, or full `governance.actions` exposure.
- No reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior changes.

## Success Criteria

- CLI summary view includes `status_summary.schema_version` when present in the detailed payload.
- HTTP summary view includes `status_summary.schema_version` when present in the detailed payload.
- Existing compact summary boundaries remain unchanged.
