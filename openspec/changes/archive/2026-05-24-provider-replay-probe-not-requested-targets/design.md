# Design: Provider Replay Probe Not Requested Targets

## Rollup

`_build_provider_replay_probe_summary()` already iterates through `PROVIDER_REPLAY_STATUS_PROBE_KEYS` in stable order and builds `requested`, `healthy`, and `unhealthy` lists.

Add a parallel `not_requested` list. A probe target is added when its normalized status is `not_requested`.

## Boundary

The new field is additive and derived from existing normalized probe objects. It does not request probes, start a replay service, change endpoint behavior, or manage daemon lifecycle.

## Testing

Add focused coverage for:

- default no-probe status containing every probe target in `not_requested`;
- partial probe status listing the skipped targets;
- CLI summary view preserving the copied `not_requested` list.
