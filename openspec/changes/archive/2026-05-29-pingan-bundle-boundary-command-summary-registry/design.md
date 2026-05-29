## Context

Selected bundle plan/preview summary views are non-executing. They resolve the selected steps and attach per-step `trade_plan_boundary` where a step maps to a known trade command. D-08 submit-once bundles can use side rollups because submit-once boundaries carry `side`; D-07 buy/sell/confirm_current needs a command rollup instead.

## Goals / Non-Goals

Goals:

- Add a compact list of unique trade commands represented by selected bundle step boundaries.
- Derive the list only from already-built step `trade_plan_boundary` objects.
- Mirror the value into `selected_step_summary` and `plan_summary` for stable summary inspection.

Non-goals:

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not add `catalog run` behavior or any new desktop trading primitive.
- Do not claim broker readiness, trading safety approval, or complete dialog/exception coverage.

## Decisions

- Extend the existing trade-boundary rollup helper rather than adding a PingAn-specific path. This keeps the field generic for every selected bundle that contains supported trade boundaries.
- Sort unique command names for deterministic payloads.
- Keep `trade_plan_boundary_step_count` as the presence count and use `trade_plan_boundary_commands` as a compact identity rollup; these fields do not replace per-step detail.

## Risks / Trade-offs

- Additive fields can be mistaken for execution coverage. Mitigation: tests and FUNCTION_TREE wording explicitly preserve non-execution and readiness boundaries.
- Command identity alone does not describe full input readiness. Mitigation: existing per-step `trade_plan_boundary` still carries required/provided/missing input fields and coverage status.

## Migration Plan

No data migration. Existing payload fields remain backward compatible; the new fields are additive.
