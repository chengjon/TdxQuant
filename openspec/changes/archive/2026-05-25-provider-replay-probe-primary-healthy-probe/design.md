## Design

`_build_provider_replay_probe_summary` already builds an ordered `healthy` list using the fixed probe key order. Add `primary_healthy_probe` to the returned summary as the first item from that list, or `None` when there are no healthy probes.

The field is a compact navigation hint. It does not replace `healthy`, `healthy_count`, `healthy_reachability_counts`, or per-probe evidence, and it does not determine service health or lifecycle behavior.

## Boundary

This is a derived summary field over already-collected probe objects. It does not request additional endpoints, expose full probe payloads, inspect token or allowlist details, start a replay server, mutate provider state, or manage daemon lifecycle. `None` only means the current summary has no healthy probe in the existing healthy list.
