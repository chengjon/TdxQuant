# Add provider replay primary error sample

## Why

Provider replay probe summary already includes bounded `error_samples` plus error-sample status/probe count maps. Callers that only need a compact first failing sample identity still have to inspect the sample list.

Adding primary error sample hints makes the replay status summary easier to scan while preserving the existing replay-only boundary: no extra probes, no socket start, no provider mutation, and no daemon lifecycle management.

## What Changes

- Add `runtime.probe_summary.primary_error_sample_probe`.
- Add `runtime.probe_summary.primary_error_sample_status`.
- Derive both fields from the first item in the existing bounded `error_samples` list.
- Return `null` for both fields when no error sample exists.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]` with explicit evidence and fake-provider lifecycle boundary.
