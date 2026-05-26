# Add provider replay primary unhealthy probe

## Why

Provider replay `probe_summary` exposes `unhealthy` and its count, and already has primary hints for `requested`, `healthy`, `failed`, and `not_requested` lists. The `unhealthy` list lacks the same first-item convenience field, so consumers must inspect the list for the first unhealthy target.

E-06 remains partial fake-provider daemon work in `FUNCTION_TREE.md`. Adding `primary_unhealthy_probe` keeps the read-only status projection symmetric without adding a daemon lifecycle manager or new probe behavior.

## What Changes

- Add read-only `runtime.probe_summary.primary_unhealthy_probe` derived from the first item in the existing `unhealthy` list.
- Return `null` when no unhealthy probes exist.
- Preserve `unhealthy`, `unhealthy_count`, `failed`, and `primary_failed_probe`.
- Do not request additional probes, start sockets, mutate provider state, or manage daemon lifecycle.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Touches `tdxquant/provider_transport_replay.py` probe-summary construction.
- Adds focused provider replay status assertions and summary-view coverage.
- Updates `FUNCTION_TREE.md` as the single registry with explicit status, evidence, and boundary.

