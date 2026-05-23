# Add Provider Replay Probe Summary

## Why

Provider replay status can already include four explicit read-only probe results:
`runtime.health_probe`, `runtime.watch_status_probe`, `runtime.watch_events_probe`,
and `runtime.watch_stream_probe`. Consumers currently have to scan each probe object
to answer the basic question of whether any requested replay surface is degraded.

## What Changes

- Add `runtime.probe_summary` to provider replay status output.
- Derive the summary only from the already-normalized probe objects.
- Preserve each individual probe payload unchanged.
- Update tests and `FUNCTION_TREE.md` so E-06 remains explicit about implemented
  evidence and daemon lifecycle boundaries.

## Out of Scope

- Starting, stopping, supervising, or restarting a replay daemon.
- Adding scheduler/backoff behavior.
- Adding live market-session support.
- Changing probe HTTP requests, authentication, or token redaction behavior.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`
