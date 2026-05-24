# Design: Provider Replay Probe Total Count

## Approach

Set `total_count` in `_build_provider_replay_probe_summary()` from `len(PROVIDER_REPLAY_STATUS_PROBE_KEYS)`. This keeps the field tied to the canonical probe key list used by the existing rollup.

## Compatibility

The field is additive. Existing probe objects, counts, lists, status rollup, and summary view shape remain compatible.

## Boundaries

`total_count` is a read-only coverage scalar. It is not a signal that probes were requested, sockets were opened, a replay service is running, or lifecycle management is available.
