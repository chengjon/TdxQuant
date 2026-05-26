# Design: Subscription runtime run-id source

## Context

Both HTTP and CLI summary runtime views choose a compact `run_id` by preferring `watch_status.run_id` and falling back to `control.run_id`. The selected value is useful, but its provenance is currently implicit in helper logic.

`runtime.run_id_source` makes that provenance explicit while keeping the summary view sparse and read-only.

## Goals / Non-Goals

- Goal: expose `runtime.run_id_source="watch_status"` when `watch_status.run_id` supplies `runtime.run_id`.
- Goal: expose `runtime.run_id_source="control"` when the summary falls back to `control.run_id`.
- Goal: omit `runtime.run_id_source` when no run id is projected.
- Non-goal: infer ownership, health, freshness, readiness, or lifecycle state from the source.
- Non-goal: trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

## Decisions

- Add the field next to `runtime.run_id` in both runtime-view helpers.
- Keep the source vocabulary limited to `watch_status` and `control`.
- Preserve the existing run-id selection order.

## Risks / Trade-offs

- The field is additive and diagnostic-only. The registry and spec explicitly prevent treating it as ownership or readiness proof.

## Migration Plan

No migration required. Existing summary fields remain unchanged.

## Open Questions

None.
