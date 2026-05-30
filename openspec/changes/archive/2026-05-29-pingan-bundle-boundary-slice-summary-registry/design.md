## Context

Bundle plan/preview summary views are derived from selected steps. Existing rollups include boundary counts and commands, but callers still infer boundary presence from `trade_plan_boundary_step_count > 0`. A direct boolean improves scanability and makes selected-step ranges less ambiguous.

## Goals / Non-Goals

Goals:

- Add a direct, deterministic boolean derived from selected step boundary count.
- Mirror the boolean into `selected_step_summary` and `plan_summary`.
- Keep the field read-only and non-executing.

Non-goals:

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not alter bundle step selection semantics.
- Do not claim broker readiness, trading safety approval, or complete desktop exception coverage.

## Decisions

- Derive `has_trade_plan_boundary` in the existing rollup helper as `trade_plan_boundary_step_count > 0`. This avoids duplicating selection logic and keeps the field tied to the same selected-step basis as count and command rollups.
- Mirror into nested summaries for consistency with other selected-step metadata.

## Risks / Trade-offs

- A boolean can hide detail. Mitigation: existing count, commands, sides, and per-step `trade_plan_boundary` remain available.
- The field could be misread as readiness. Mitigation: FUNCTION_TREE boundary text explicitly states it is selected-step catalog summary evidence only.

## Migration Plan

No data migration. The field is additive.
