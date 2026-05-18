# Design

## Context

`tdxquant/provider_transport_replay.py` already provides:

- `ProviderTransportReplayConfig`
- `load_provider_transport_replay_config(...)`
- `serve_provider_transport_replay(...)`
- A read-only HTTP surface backed by replay fixtures

The missing piece is a stable CLI wrapper that can be invoked from local scripts without importing Python internals.

## Decision

Add a top-level `provider-replay` command group:

- `provider-replay serve --config runtime/provider-transport-replay.example.json`
- `provider-replay config-check --config runtime/provider-transport-replay.example.json`

`serve` loads the config and delegates directly to `serve_provider_transport_replay`. It intentionally blocks like a normal foreground server process.

`config-check` loads the same config and returns a `Result` summary containing provider id, bind host, port, allowlist count, and configured replay fixture fields. It does not start sockets.

## Non-Goals

- Do not add background process management.
- Do not add start/stop/status daemon state files.
- Do not change bearer-token or allowlist enforcement.
- Do not add live provider fallback.

