# Design: Provider replay primary unhealthy probe

## Context

`runtime.probe_summary` has list-style rollups for requested, healthy, failed, unhealthy, and not-requested probes. Primary fields already exist for most of those lists:

- `primary_requested_probe`
- `primary_healthy_probe`
- `primary_failed_probe`
- `primary_not_requested_probe`

The new field adds the same first-item hint for `unhealthy`.

## Goals / Non-Goals

- Goal: expose `primary_unhealthy_probe` as the first value in `unhealthy`.
- Goal: expose `null` when `unhealthy` is empty.
- Non-goal: change failed/unhealthy classification or ordering.
- Non-goal: request additional probes, start sockets, mutate providers, schedule retry/backoff, or manage daemon lifecycle.

## Decisions

- Derive the field at the same return-site as the existing primary probe hints.
- Keep `primary_failed_probe` unchanged even though current failed and unhealthy lists share the same entries.
- Allow CLI summary view to inherit the field through its existing `probe_summary` projection.

## Risks / Trade-offs

- `primary_unhealthy_probe` can be mistaken for a new probe result. The registry and spec state it is only a convenience hint derived from the existing `unhealthy` list.

## Migration Plan

No migration required. Existing fields remain unchanged.

## Open Questions

None.

