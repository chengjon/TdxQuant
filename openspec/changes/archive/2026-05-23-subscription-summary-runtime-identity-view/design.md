## Context

Bridge watch-status detailed responses contain `control` and `watch_status`
objects. The existing summary views intentionally avoid copying those raw
objects, but they also omit compact run identity fields that help an operator
tie a summary to the active controller/run. B-16/E-09 should remain a read-only
status projection, so the change must not introduce lifecycle actions or
change reconnection behavior.

## Goals / Non-Goals

- Add a compact `runtime` object to CLI and HTTP summary views.
- Derive `runtime` only from existing detailed `control` and `watch_status` data.
- Include selected scalar identity fields: control state/activity, watch state, run id, and pid when present.
- Preserve default detailed responses and avoid exposing raw `control`/`watch_status` objects in summary mode.
- Do not start, stop, restart, reconnect, back off, probe, mutate files, or alter event-stream behavior.

## Decisions

- Use a new `runtime` object rather than adding more top-level fields.
  - Rationale: it keeps summary payloads compact and avoids mixing identity fields with governance status.
  - Alternative considered: copy raw `control`/`watch_status` into summary output. That would defeat the summary boundary and leak detailed internals.
- Prefer `watch_status.run_id` when present, falling back to `control.run_id`.
  - Rationale: persisted watch status identifies the active watch run, while control state is a reasonable fallback when status has not yet been written.
- Keep missing fields absent instead of filling synthetic defaults.
  - Rationale: missing identity data should be distinguishable from an observed false or empty value.

## Risks / Trade-offs

- Consumers may treat runtime identity as lifecycle control state. Mitigation: specs and FUNCTION_TREE boundary state that the projection is read-only and does not manage lifecycle.
- CLI and HTTP summary helpers are duplicated. Mitigation: keep the projection logic small and covered by both CLI and HTTP tests; avoid broader refactoring in this slice.

## Migration Plan

No migration is required. Existing detailed responses remain the default, and summary responses only gain additive `runtime` fields when source data is present.

## Open Questions

None.
