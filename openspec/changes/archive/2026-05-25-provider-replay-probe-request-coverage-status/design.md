## Design

`_build_provider_replay_probe_summary` already computes `requested_count` and the fixed `total_count`. Add a small helper branch after `requested_count` is known:

- `none` when no probes were requested.
- `partial` when at least one but not all probes were requested.
- `complete` when all known replay probes were requested.

The value is independent from health: a complete probe set may still be degraded, and a partial probe set may have all requested probes healthy. The CLI summary view copies `probe_summary`, so no separate projection logic is needed beyond tests that pin the field.

## Boundary

- Derived only from existing resolved probe objects.
- Does not request additional probes.
- Does not start sockets, manage daemon lifecycle, schedule probes, restart processes, or mutate provider state.
- Does not prove health, endpoint coverage, or replay fidelity.
