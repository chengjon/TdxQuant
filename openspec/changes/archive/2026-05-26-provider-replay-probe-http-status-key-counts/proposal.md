## Why

Provider replay probe summary already exposes requested, healthy, and failed HTTP status count maps. Explicit key-count fields make the HTTP status rollup easier to consume without requiring callers to recompute map lengths.

## What Changes

- Add `runtime.probe_summary.requested_http_status_key_count` derived from `requested_http_status_counts`.
- Add `runtime.probe_summary.healthy_http_status_key_count` derived from `healthy_http_status_counts`.
- Add `runtime.probe_summary.failed_http_status_key_count` derived from `failed_http_status_counts`.
- Keep the fields additive and read-only; they do not request probes, start sockets, mutate providers, or manage daemon lifecycle.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: Provider replay status exposes additive probe HTTP status key-count fields derived from already projected HTTP status count maps.

## Impact

- `tdxquant/provider_transport_replay.py`: probe summary projection adds three derived count fields.
- `tests/test_provider_transport_replay.py`: provider replay status tests assert the new fields and no-lifecycle boundary.
- `FUNCTION_TREE.md`: E-06 evidence/boundary registry is updated without promoting daemon fake provider to fully implemented.
