## Design

`_build_provider_replay_probe_summary()` already iterates over the fixed provider replay probe keys and normalizes missing probe objects to `not_requested`. This change adds a second count map:

- `status_counts` continues to count every fixed probe, including `not_requested`;
- `requested_status_counts` increments only after the probe is classified as requested;
- the returned map is sorted for deterministic JSON output;
- empty/no-probe status returns `{}`.

Because CLI summary view deep-copies `probe_summary`, the new field is preserved there without extra lifecycle behavior.

## Boundaries

- `requested_status_counts` is read-only aggregate metadata.
- It does not request additional probes, change existing probe flags, or alter probe URLs.
- It does not start, stop, restart, daemonize, supervise, or schedule the replay service.
- It does not expose raw probe payloads, tokens, or allowlist members.

