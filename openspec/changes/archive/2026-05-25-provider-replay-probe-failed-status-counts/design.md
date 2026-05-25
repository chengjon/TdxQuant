## Context

`_build_provider_replay_probe_summary()` already iterates over the fixed provider replay probe keys and derives requested, healthy, failed, unhealthy, not-requested, `status_counts`, `requested_status_counts`, `error_code_counts`, and bounded error samples. The new field can be computed in that same pass without changing probe execution or the CLI surface.

## Goals / Non-Goals

- Goal: expose `runtime.probe_summary.failed_status_counts` as a sorted count map for requested probe statuses that are not `healthy`.
- Goal: preserve `failed`, `failed_count`, `unhealthy`, `requested_status_counts`, and summary view behavior.
- Non-goal: adding new probe targets, changing probe transport, starting sockets, managing daemon lifecycle, or treating the count map as health/readiness automation.

## Decisions

- Count only requested probes whose normalized status is not `healthy`. This excludes both `healthy` and `not_requested`, matching the field name and avoiding duplication with `requested_status_counts`.
- Reuse the existing stable probe-key loop and sorted-map return style. This keeps output deterministic and follows the current status-count conventions.
- Do not add a separate CLI projection layer. The summary view already includes the complete `probe_summary`, so adding the field to the derived probe summary is enough.

## Risks / Trade-offs

- The new field overlaps with `requested_status_counts`. Mitigation: document the boundary clearly as a failed-only diagnostic distribution.
- A future status taxonomy could add more non-healthy statuses. Mitigation: count any requested status other than `healthy` instead of hard-coding a fixed failure set.

## Migration Plan

The field is additive. Existing callers that ignore unknown keys continue working. Rollback removes the field and associated tests/spec delta.

## Open Questions

None.
