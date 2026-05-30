## Context

Submit-once bundle plan/preview summary views expose per-step `trade_plan_boundary`, side rollups, command rollups, boundary presence, and now input coverage status counts through the generic catalog summary helper. D-08 needs explicit evidence and boundary text for that surface.

## Goals / Non-Goals

Goals:

- Pin submit-once bundle coverage-status summary behavior with tests.
- Register the evidence in D-08 without moving the feature to implemented.
- Keep boundaries clear that the summary is non-executing and selected-step based.

Non-goals:

- Do not change catalog execution, bundle dispatch, or desktop trading behavior.
- Do not add `catalog run --side`.
- Do not claim broker readiness, trading safety approval, or complete dialog/exception coverage.

## Decisions

- Treat this as a registry/test alignment slice. The behavior already exists through the generic rollup, so implementation code does not need to change.
- Cover both buy and sell submit-once bundles and an excluded-step range to show selected-step scoping.

## Risks / Trade-offs

- Registry-only changes can look like a roadmap claim. Mitigation: D-08 remains `[部分实现]` and boundary text states the evidence is read-only and non-executing.

## Migration Plan

No migration. No runtime behavior change.
