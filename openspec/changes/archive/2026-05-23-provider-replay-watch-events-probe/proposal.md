## Why

E-06 now exposes health and watch-status probes for an already-running provider replay service, but the fake provider event projection is still only discoverable by manually calling `/provider/v1/replay/watch/events`. A status-time opt-in watch-events probe lets operators verify the replay event surface without implying daemon lifecycle management.

## What Changes

- Add `probe_provider_transport_replay_watch_events()` for `/provider/v1/replay/watch/events`.
- Add `--probe-watch-events` to `provider-replay status`.
- Include the optional watch-events probe result in `build_provider_transport_replay_status(...).runtime`.
- Keep the probe read-only and opt-in; status still never starts, stops, restarts, or daemonizes a replay service.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: expose an optional watch-events surface probe for provider replay lifecycle status.

## Impact

- Runtime code: `tdxquant/provider_transport_replay.py`
- CLI: `tdxquant/cli.py`
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
