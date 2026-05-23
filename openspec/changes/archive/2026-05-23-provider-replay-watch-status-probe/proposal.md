## Why

E-06 already exposes replay service configuration status and an optional health probe, but health only proves the service endpoint responds. Operators need an equally explicit read-only probe for the fake provider watch-status surface so `provider-replay status` can distinguish "service is healthy" from "watch-status fixture projection is reachable."

## What Changes

- Add `probe_provider_transport_replay_watch_status()` for `/provider/v1/replay/watch/status`.
- Add `--probe-watch-status` to `provider-replay status`.
- Include the optional watch-status probe result in `build_provider_transport_replay_status(...).runtime`.
- Preserve the existing lifecycle boundary: no start/stop, daemon management, scheduler, restart, or live market session behavior.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: expose an optional watch-status surface probe for provider replay lifecycle status.

## Impact

- Runtime code: `tdxquant/provider_transport_replay.py`
- CLI: `tdxquant/cli.py`
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
