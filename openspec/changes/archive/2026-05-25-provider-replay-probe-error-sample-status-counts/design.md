## Design

Extend `_build_provider_replay_probe_summary()` with a local `error_sample_status_counts` map. Whenever a probe qualifies for the existing error sample candidate set, increment the count for that probe's normalized status. The map is sorted by status key in the returned payload.

This keeps three related but distinct rollups:

- `failed_status_counts`: requested non-healthy probes only.
- `error_sample_count`: total probe results that qualified for the compact error sample candidate set.
- `error_sample_status_counts`: status distribution of that same error sample candidate set.

The summary view already projects the full `probe_summary`, so no separate view-specific transformation is needed.

## Boundaries

- This is a compact diagnostic rollup, not the full probe payload.
- It does not prove failure coverage or health coverage.
- It does not start, stop, restart, daemonize, schedule, supervise, or mutate a provider.
