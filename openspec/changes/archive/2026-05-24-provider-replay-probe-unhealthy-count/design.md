# Design: Provider Replay Probe Unhealthy Count

## Approach

Extend `_build_provider_replay_probe_summary()` with `unhealthy_count = len(unhealthy)` after the canonical probe loop builds the target lists. Keep `failed_count` as an existing compatibility field and return the new count next to the other probe count scalars.

Because `_build_provider_replay_status_summary_view()` already deep-copies `runtime.probe_summary`, the new scalar flows into the opt-in CLI summary view without exposing additional probe details or changing runtime observation.

## Compatibility

This is an additive status field. Existing consumers of `failed_count`, `status_counts`, and the target lists keep the same payload shape and semantics.

## Boundaries

`unhealthy_count` is a read-only rollup over already-normalized probe states. It does not request probes, start sockets, mark a daemon unhealthy, manage lifecycle, restart services, or imply live replay availability.
