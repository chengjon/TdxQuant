# Add provider replay visible error sample count

## Why

Provider replay probe summary exposes total error sample candidates, hidden sample count, sample limit, and the bounded `error_samples` list. Callers can count the visible sample list themselves, but the summary does not expose that value as a stable field.

Adding `error_sample_visible_count` makes the sample rollup explicit while preserving the existing replay-only boundary: no extra probes, no full probe payload exposure, no socket start, no provider mutation, and no daemon lifecycle management.

## What Changes

- Add `runtime.probe_summary.error_sample_visible_count`.
- Derive it as `len(error_samples)`.
- Keep `error_sample_count`, `error_sample_hidden_count`, `error_sample_limit`, and `error_sample_truncated` semantics unchanged.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Code: `tdxquant/provider_transport_replay.py`
- Tests: `tests/test_provider_transport_replay.py`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
- Registry: `FUNCTION_TREE.md` E-06 remains `[部分实现]` with explicit evidence and fake-provider lifecycle boundary.
