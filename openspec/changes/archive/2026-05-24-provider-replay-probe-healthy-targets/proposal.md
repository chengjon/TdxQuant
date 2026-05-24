## Why

E-06 provider replay status already reports requested probes, unhealthy probes, and status counts, but operators cannot see the healthy probe targets from the compact rollup without reading each individual probe object. A `healthy` target list keeps the fake-provider status summary easier to audit while preserving its replay-only, read-only boundary.

## What Changes

- Add `runtime.probe_summary.healthy` to provider replay status.
- Derive the list from existing probe objects whose status is `healthy`.
- Preserve existing `requested`, `unhealthy`, counts, lifecycle boundary, and probe behavior.
- Keep the provider replay summary read-only: no socket start, no daemon control, no scheduler/restart governance, and no write capability.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: provider replay probe summary includes healthy probe target names.

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
