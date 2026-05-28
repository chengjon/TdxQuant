## Context

`FUNCTION_TREE.md` is the single feature registry. E-06's detailed supplemental notes now show a completed replay daemon lifecycle surface, while the main row remains stale. This change only reconciles the registry.

## Goals / Non-Goals

**Goals:**

- Make E-06 status match implemented replay fake provider lifecycle evidence.
- Keep evidence paths concrete and validator-friendly.
- Keep the boundary tight so readers do not infer live TongDaXin provider lifecycle, workflow readiness, or write capability.

**Non-Goals:**

- No source behavior change.
- No daemon process launch, stop, restart, or supervision during validation.
- No cleanup of unrelated dirty files.
- No changes to D-07/D-08, B-16/E-09, real broker, trade, or write paths.

## Decisions

- Replace the E-06 main row rather than relying only on appended supplemental notes. The main registry row is the primary reader entry point and must not contradict the implemented supplements.
- Keep the status as `[已实现]` only for the named node, `daemon fake provider`, because implemented evidence is specific to replay provider lifecycle control and diagnostics.
- Keep the boundary explicit: replay HTTP/runtime surfaces can be started and managed, but this does not prove real provider availability, broker readiness, workflow readiness, or write support.

## Risks / Trade-offs

- [Risk] `[已实现]` may be read too broadly. -> Mitigation: the boundary cell and supplemental note explicitly limit implementation to replay fake provider lifecycle.
- [Risk] The main row becomes too terse compared with historical supplements. -> Mitigation: cite the core files, tests, and latest OpenSpec changes while preserving detailed supplements below the table.
