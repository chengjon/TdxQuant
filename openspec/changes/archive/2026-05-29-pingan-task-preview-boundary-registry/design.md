# Design

## Scope

This is a read-only catalog registration slice for D-07. The implementation already routes `catalog preview` through the same planning path as `catalog plan`; this change pins the behavior with tests and updates the registry wording.

## Behavior

`catalog preview --entry task-buy --view summary` and `catalog preview --entry task-confirm-current --view summary` should expose `trade_plan_boundary` with:

- `execution_mode=non_executing_catalog_plan`
- `dispatch_executed=false`
- command-specific `trade_command`
- derived required/provided/missing input fields and counts

For `task-buy`, the boundary remains an order input boundary. For `task-confirm-current`, the boundary remains a confirmation boundary with no required order inputs.

## Boundary

D-07 remains `[部分实现]`. Preview is an inspection view only. It must not dispatch task/trade/report/bundle steps and must not imply broker readiness, trading safety approval, direct trade catalog execution, or complete desktop exception coverage.

## Test Strategy

Add focused API CLI tests for preview parity and a FUNCTION_TREE registry test that fails until D-07 evidence names `catalog plan/preview` and keeps the non-execution boundary.
