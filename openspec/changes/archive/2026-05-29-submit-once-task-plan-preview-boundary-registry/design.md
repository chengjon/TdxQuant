# Design

## Scope

This is a D-08 registry and test hardening change for existing read-only catalog behavior. It does not modify submit-once desktop execution, does not introduce a new `run_pingan_sell_submit_once` primitive, and does not expand `catalog run`.

## Behavior

The existing catalog planner resolves task presets through `_build_task_preset_namespace()` and projects `trade_plan_boundary` when the resolved task command is `trade-submit-once`. This change pins that behavior for:

- `catalog plan --entry task-buy-submit-once --view summary`
- `catalog preview --entry task-buy-submit-once --view summary`
- `catalog plan --entry task-sell-submit-once --view summary`
- `catalog preview --entry task-sell-submit-once --view summary`

Each boundary should be non-executing, not dispatched, and include the preset-owned side (`buy` or `sell`) plus derived order input coverage.

## Boundary

D-08 remains `[部分实现]`. Plan/preview only inspect resolved catalog input coverage. They do not run task/trade/report/bundle steps, do not prove broker readiness, do not approve trading safety, and do not add or prove separate desktop execution primitives.

## Test Strategy

Add API CLI tests for buy/sell submit-once task plan/preview summary projections. Add a FUNCTION_TREE registry test that fails until D-08 names those plan/preview entries and keeps the non-execution boundary.
