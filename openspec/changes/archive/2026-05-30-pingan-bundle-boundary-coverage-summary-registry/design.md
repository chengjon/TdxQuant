## Context

Each selected trade step can expose `trade_plan_boundary.input_coverage_status`. Existing bundle rollups expose count, command list, side list, and presence. A status-count map lets maintainers quickly inspect selected bundle input coverage without reading every step.

## Goals / Non-Goals

Goals:

- Add deterministic counts keyed by `input_coverage_status`.
- Derive counts only from selected step `trade_plan_boundary` objects.
- Mirror counts into `selected_step_summary` and `plan_summary`.

Non-goals:

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not validate option semantics or broker readiness.
- Do not change selected-step range semantics or required input definitions.

## Decisions

- Extend the existing trade-boundary rollup helper. It already receives selected step views and is the single source for boundary count/command/presence rollups.
- Sort map keys for deterministic payloads.
- Omit invented statuses; selected ranges with no trade boundary return an empty map and `has_trade_plan_boundary=false`.

## Risks / Trade-offs

- A count map can be mistaken for readiness proof. Mitigation: FUNCTION_TREE boundary states it is a selected-step catalog summary only.
- Empty maps can be ambiguous. Mitigation: `has_trade_plan_boundary` and `trade_plan_boundary_step_count` remain present to distinguish no selected boundary from complete coverage.

## Migration Plan

No data migration. The field is additive.
