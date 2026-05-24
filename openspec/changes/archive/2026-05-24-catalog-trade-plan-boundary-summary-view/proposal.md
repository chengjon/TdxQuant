# catalog-trade-plan-boundary-summary-view

## Why

`FUNCTION_TREE.md` D-07/D-08 record PingAn trade entry and submit-once catalog coverage as partial. Catalog plan/preview can already resolve fixed trade entries and bundles without execution, but summary readers still have to infer whether the visible plan is a real trade action or only a non-executing plan.

This change adds an explicit trade plan boundary to catalog summary views for trade-related entries and selected bundle steps. The boundary shows the resolved trade command, input field coverage, and non-execution posture.

## What Changes

- Add `trade_plan_boundary` to trade-related entry plan/preview summary views.
- Add per-step `trade_plan_boundary` to trade-related bundle plan/preview summary steps.
- Include required/provided/missing key input fields for order-like trade commands.
- Keep catalog plan/preview non-executing and keep `catalog run` behavior unchanged.
- Update `FUNCTION_TREE.md` D-07/D-08 evidence and boundary.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Runtime behavior: no live broker calls, dispatch execution, or `catalog run` changes.
- Safety: summary explicitly states `execution_mode=non_executing_catalog_plan` and `dispatch_executed=false`.
- Registry: `FUNCTION_TREE.md` remains the single feature/status registry.

