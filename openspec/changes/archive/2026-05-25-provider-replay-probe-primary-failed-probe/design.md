## Design

`_build_provider_replay_probe_summary` already builds an ordered `failed` list using the fixed probe key order. Add `primary_failed_probe` to the returned summary as the first item from that list, or `None` when there are no failed probes.

The field is a compact navigation hint. It does not replace `failed`, `failed_count`, `failed_status_counts`, or error samples, and it does not determine health or lifecycle behavior.

## Boundary

- Derived only from existing resolved probe objects.
- Uses the same ordering and unhealthy classification as the existing `failed` list.
- Does not request additional probes.
- Does not start sockets, manage daemon lifecycle, schedule probes, restart processes, or mutate provider state.
- Does not prove health, endpoint coverage, or replay fidelity.
