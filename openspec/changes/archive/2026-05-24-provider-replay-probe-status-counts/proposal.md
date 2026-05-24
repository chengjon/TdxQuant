## Why

E-06 now exposes provider replay probe rollups, but callers still need to inspect multiple count fields to understand probe status composition. A compact `status_counts` object makes the fake provider status easier to scan while keeping the replay transport read-only.

## What Changes

- Add `runtime.probe_summary.status_counts` to provider replay status payloads.
- Derive counts from the fixed replay probe statuses (`health`, `watch_status`, `watch_events`, `watch_stream`).
- Preserve existing `requested_count`, `healthy_count`, `failed_count`, `not_requested_count`, `requested`, and `unhealthy` fields.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: provider replay probe summary exposes compact status counts.

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.
