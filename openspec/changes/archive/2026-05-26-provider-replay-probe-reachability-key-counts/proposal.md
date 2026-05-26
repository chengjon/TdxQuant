## Why

Provider replay probe summary already exposes requested, healthy, and failed reachability count maps. Explicit key-count fields make the read-only reachability rollup easier to consume without requiring callers to recompute map lengths.

## What Changes

- Add `runtime.probe_summary.requested_reachability_key_count` derived from `requested_reachability_counts`.
- Add `runtime.probe_summary.healthy_reachability_key_count` derived from `healthy_reachability_counts`.
- Add `runtime.probe_summary.failed_reachability_key_count` derived from `failed_reachability_counts`.
- Keep the fields additive and read-only; they do not request probes, start sockets, mutate providers, or manage daemon lifecycle.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: Provider replay status exposes additive probe reachability key-count fields derived from already projected reachability count maps.

## Impact

- `tdxquant/provider_transport_replay.py`: probe summary projection adds three derived count fields.
- `tests/test_provider_transport_replay.py`: provider replay status tests assert the new fields and no-lifecycle boundary.
- `FUNCTION_TREE.md`: E-06 evidence/boundary registry is updated without promoting daemon fake provider to fully implemented.
