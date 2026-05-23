## Why

`provider-replay status --config` currently reports only static replay configuration and boundary metadata. E-06 needs a safer intermediate state: callers should be able to explicitly probe whether the configured replay HTTP service is reachable without implying daemon lifecycle ownership.

## What Changes

- Add an opt-in provider replay health probe for the configured replay HTTP service.
- Extend `provider-replay status` with explicit probe flags while keeping the default status path network-free.
- Include probe result metadata in the lifecycle status without exposing bearer tokens.
- Keep the capability read-only and non-governing: no start, stop, restart, scheduler, or live market session behavior is added.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: status may optionally probe the configured replay health endpoint and report the observed replay-service health boundary.

## Impact

- `tdxquant/provider_transport_replay.py`
- `tdxquant/cli.py`
- `tests/test_provider_transport_replay.py`
- `tests/test_api_cli.py`
- `FUNCTION_TREE.md`
