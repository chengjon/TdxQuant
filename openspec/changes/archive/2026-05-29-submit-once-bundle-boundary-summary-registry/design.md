## Context

Catalog bundle plan/preview summary views already resolve selected bundle steps without dispatching them. Trade-related steps may include a per-step `trade_plan_boundary`, but callers must inspect the `steps` list to derive a quick answer about whether trade boundaries are present and which submit-once side appears in the selected bundle.

## Goals / Non-Goals

Goals:

- Add a small read-only rollup for selected bundle steps that already contain `trade_plan_boundary`.
- Keep the rollup deterministic and derived only from summary data already built for the selected steps.
- Preserve D-08 as partial because this is catalog inspection evidence, not execution readiness.

Non-goals:

- Do not execute catalog entries, tasks, reports, trades, or bundle steps.
- Do not add `catalog run --side` or any new desktop trading primitive.
- Do not claim broker readiness, trading safety approval, or complete dialog/exception coverage.

## Decisions

- Derive rollup fields from `plan_steps` after per-step `trade_plan_boundary` construction. This avoids reparsing presets or duplicating trade command knowledge.
- Expose `trade_plan_boundary_step_count` as a count and `trade_plan_boundary_sides` as a sorted unique list of string sides. This is enough for buy/sell submit-once bundle inspection while staying compact.
- Mirror the fields into `plan_summary` through `selected_step_summary` so both top-level summary and the stable nested summary view carry the same read-only signal.

## Risks / Trade-offs

- Additive summary fields can be mistaken for readiness evidence. Mitigation: tests and FUNCTION_TREE boundary text explicitly say the fields are non-executing and not broker/safety readiness.
- Empty side lists on non-submit trade steps could be ambiguous. Mitigation: `trade_plan_boundary_step_count` remains the presence indicator; `trade_plan_boundary_sides` only reports sides that are explicitly present.

## Migration Plan

No data migration. Existing detailed and summary payloads remain backward compatible with additive fields.
