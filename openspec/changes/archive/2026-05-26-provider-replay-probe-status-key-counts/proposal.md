## Why

Provider replay probe summary already exposes `status_counts`, `requested_status_counts`, and `failed_status_counts`. Explicit key-count fields make the read-only probe rollup easier to consume without requiring callers to recompute map lengths.

## What Changes

- Add `runtime.probe_summary.status_key_count` derived from `status_counts`.
- Add `runtime.probe_summary.requested_status_key_count` derived from `requested_status_counts`.
- Add `runtime.probe_summary.failed_status_key_count` derived from `failed_status_counts`.
- Keep the fields additive and read-only; they do not request probes, start sockets, mutate providers, or manage daemon lifecycle.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: Provider replay status exposes additive probe status key-count fields derived from already projected status count maps.

## Impact

- `tdxquant/provider_transport_replay.py`: probe summary projection adds three derived count fields.
- `tests/test_provider_transport_replay.py`: provider replay status tests assert the new fields and non-lifecycle boundary.
- `FUNCTION_TREE.md`: E-06 evidence/boundary registry is updated without promoting daemon fake provider to fully implemented.
