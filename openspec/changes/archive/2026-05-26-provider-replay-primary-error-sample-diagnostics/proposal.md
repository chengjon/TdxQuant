# Add provider replay primary error sample diagnostics

## Why

Provider replay probe summary now exposes primary error sample probe and status hints derived from the first bounded error sample. The first sample can also carry an `error_code` and `http_status`, but callers still need to inspect the bounded sample list to get those compact diagnostics.

Adding primary error sample diagnostic hints keeps summary output easy to scan while preserving the replay-only boundary: no extra probes, no full probe payload exposure, no socket start, no provider mutation, and no daemon lifecycle management.

## What Changes

- Add `runtime.probe_summary.primary_error_sample_error_code`.
- Add `runtime.probe_summary.primary_error_sample_http_status`.
- Derive both fields from the first item in the existing bounded `error_samples` list.
- Return `null` for missing/non-string error codes and missing/non-integer HTTP status values.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]` with explicit evidence and fake-provider lifecycle boundary.
