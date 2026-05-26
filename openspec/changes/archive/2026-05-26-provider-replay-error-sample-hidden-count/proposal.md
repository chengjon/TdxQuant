# Add provider replay hidden error sample count

## Why

Provider replay probe summary exposes bounded `error_samples`, the total `error_sample_count`, the sample limit, and whether the list was truncated. Callers can infer how many candidate samples were hidden, but the summary does not expose that value directly.

Adding `error_sample_hidden_count` gives callers a compact truncation magnitude while preserving the existing replay-only boundary: no extra probes, no full probe payload exposure, no socket start, no provider mutation, and no daemon lifecycle management.

## What Changes

- Add `runtime.probe_summary.error_sample_hidden_count`.
- Derive it as `max(error_sample_count - len(error_samples), 0)`.
- Keep `error_sample_count`, `error_sample_limit`, and `error_sample_truncated` semantics unchanged.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]` with explicit evidence and fake-provider lifecycle boundary.
