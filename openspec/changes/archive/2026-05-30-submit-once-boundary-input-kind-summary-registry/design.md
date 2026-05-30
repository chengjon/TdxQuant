## Context

`trade_plan_boundary_input_kind_counts` is a generic catalog plan/preview summary rollup derived from selected steps with `trade_plan_boundary`. D-08 needs explicit registry coverage for submit_once bundles so readers can see that buy/sell submit_once parsing remains non-executing and is identified as `submit_once_order`.

## Goals / Non-Goals

**Goals:**

- Add D-08-specific tests for submit_once bundle input-kind summary output.
- Register the evidence in `FUNCTION_TREE.md`.
- Keep D-08 as `[部分实现]`.

**Non-Goals:**

- Do not change submit_once execution behavior.
- Do not add `catalog run --side`.
- Do not claim broker readiness, trading safety approval, production readiness, or independent desktop submit_once primitives.

## Decisions

- Use existing plan/preview summary output and assert `submit_once_order` for both buy and sell submit_once bundles.
- Assert `{}` for selected step ranges that exclude the trade step.
- Treat this as a registry/test alignment slice; no new execution code is required unless tests reveal a regression.

## Risks / Trade-offs

- Because the generic rollup already exists, the API behavior test may pass before registry update. The red test target is still meaningful because `FUNCTION_TREE.md` must explicitly register the evidence before the feature registry can be trusted.
