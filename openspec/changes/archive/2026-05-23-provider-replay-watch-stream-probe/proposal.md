## Why

E-06 records that the fake provider can project watch status, watch events, and SSE frames. Status now has opt-in probes for health, watch status, and watch events; the SSE surface remains visible only by directly calling the stream endpoint.

Adding a watch-stream probe completes the read-only provider replay surface checks while keeping the daemon boundary explicit.

## What Changes

- Add `probe_provider_transport_replay_watch_stream()` for `/provider/v1/replay/watch/events/stream`.
- Add `--probe-watch-stream` to `provider-replay status`.
- Include the optional watch-stream probe result in `build_provider_transport_replay_status(...).runtime`.
- Validate only that the SSE response is reachable and contains frames; do not change event-stream semantics.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: expose an optional watch-stream surface probe for provider replay lifecycle status.

## Impact

- Runtime code: `tdxquant/provider_transport_replay.py`
- CLI: `tdxquant/cli.py`
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
