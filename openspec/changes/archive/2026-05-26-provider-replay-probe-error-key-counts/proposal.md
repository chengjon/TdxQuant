## Why

Provider replay probe summary already exposes error-code and compact error-sample count maps. Explicit key-count fields make those read-only diagnostics easier to consume without requiring callers to recompute map lengths or inspect the sample payload.

## What Changes

- Add `runtime.probe_summary.error_code_key_count` derived from `error_code_counts`.
- Add `runtime.probe_summary.failed_error_code_key_count` derived from `failed_error_code_counts`.
- Add `runtime.probe_summary.error_sample_status_key_count` derived from `error_sample_status_counts`.
- Add `runtime.probe_summary.error_sample_probe_key_count` derived from `error_sample_probe_counts`.
- Keep the fields additive and read-only; they do not request probes, expose full error payloads, mutate providers, or manage daemon lifecycle.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: Provider replay status exposes additive probe error-code and error-sample key-count fields derived from already projected count maps.

## Impact

- `tdxquant/provider_transport_replay.py`: probe summary projection adds four derived count fields.
- `tests/test_provider_transport_replay.py`: provider replay status tests assert the new fields and no-lifecycle boundary.
- `FUNCTION_TREE.md`: E-06 evidence/boundary registry is updated without promoting daemon fake provider to fully implemented.
