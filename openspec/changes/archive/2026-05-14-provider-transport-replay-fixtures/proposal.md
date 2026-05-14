## Why

The replay provider can already serve in-process fixtures, and the bridge can now expose subscription events over HTTP/SSE, but offline transport consumers still lack a minimal HTTP replay surface that behaves like a daemon-backed provider without touching live Windows runtime state.

## What Changes

- Add a fixture-backed HTTP replay service that exposes a small, read-only provider transport surface for supported replay assets.
- Add daemon fake-provider semantics for subscription-watch transport endpoints so tests can exercise bridge-style status, events, and SSE frames without a live TongDaXin session.
- Add delayed playback support for replay event streams using deterministic fixture metadata, while keeping immediate playback as the default.
- Extend replay fixtures with a delayed playback sample and transport replay metadata.
- Preserve existing CLI subprocess replay behavior and avoid adding new business capabilities.

## Capabilities

### New Capabilities
- `tdx-provider-transport-replay-service`: Fixture-backed HTTP replay service, daemon fake-provider semantics, and delayed playback contracts for offline transport validation.

### Modified Capabilities
- `tdx-provider-replay-fixtures`: Replay fixture catalog gains transport replay metadata and delayed playback samples.
- `tdx-provider-replay-mode`: Replay mode gains strict transport replay semantics without live fallback.
- `tdx-worker-bridge-http-control-plane`: HTTP/SSE bridge contracts gain explicit replay-service parity boundaries for the subset mirrored by the fake provider.

## Impact

- Affected code: replay provider helpers, replay fixture catalog, a new transport replay service module, and focused transport tests.
- Affected fixtures: provider replay samples under `tdxquant/fixtures/provider/`.
- Affected specs: replay fixtures, replay mode, bridge HTTP control plane, and the new transport replay service capability.
- No live Windows runtime, business capability, or existing CLI subprocess replay contract should change.
