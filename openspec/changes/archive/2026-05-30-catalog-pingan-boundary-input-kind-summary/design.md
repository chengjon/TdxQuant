## Context

Catalog plan/preview summary output already derives trade boundary rollups from selected non-executing steps: boundary count, commands, sides, and input coverage status. Each boundary also carries `input_kind`, but consumers must inspect individual steps to distinguish order-style buy/sell boundaries from confirmation boundaries.

## Goals / Non-Goals

**Goals:**

- Add a deterministic `trade_plan_boundary_input_kind_counts` map derived from selected steps.
- Keep the field available in top-level summary, `selected_step_summary`, and `plan_summary`.
- Register D-07 evidence without changing D-07 status.

**Non-Goals:**

- Do not execute task, trade, report, or bundle steps.
- Do not add `catalog run` behavior.
- Do not claim broker readiness, trading safety approval, production readiness, or complete desktop exception coverage.
- Do not change the underlying PingAn desktop execution primitives.

## Decisions

- Count only selected steps that already have `trade_plan_boundary`.
- Use each boundary's existing `input_kind` value as the count key, for example `order` and `confirmation`.
- Return `{}` when the selected step range excludes trade/confirm boundaries.

## Risks / Trade-offs

- This is another summary projection, not new execution functionality. The `FUNCTION_TREE.md` boundary must remain explicit so readers do not infer D-07 is implemented.
