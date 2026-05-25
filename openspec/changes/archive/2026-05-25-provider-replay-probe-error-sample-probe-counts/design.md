## Design

Extend `_build_provider_replay_probe_summary()` with a local `error_sample_probe_counts` map. Whenever a probe qualifies for the existing compact error sample candidate set, increment the count for that probe key. The map is sorted by probe key in the returned payload.

This keeps the related rollups distinct:

- `error_sample_count`: total probe results that qualified for compact error samples.
- `error_sample_status_counts`: status distribution of those candidates.
- `error_sample_probe_counts`: probe-key distribution of those candidates, independent of the bounded `error_samples` list.

The summary view already projects the full `probe_summary`, so no separate view-specific transformation is needed.

## Boundaries

- This is a compact diagnostic rollup, not the full probe payload.
- It does not prove failure coverage or health coverage.
- It does not start, stop, restart, daemonize, schedule, supervise, or mutate a provider.

