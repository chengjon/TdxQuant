# Design

## Scope

This is a D-07 registry and test hardening change for existing read-only catalog behavior. It does not add a new catalog source, does not enable direct `trade-buy` / `trade-sell` catalog entries, and does not expand `catalog run`.

## Behavior

The existing catalog planner resolves task presets through `_build_task_preset_namespace()` and projects `trade_plan_boundary` when the resolved command is a known trading command. This change pins that behavior for:

- `catalog plan --entry task-buy --view summary`
- `catalog plan --entry task-sell --view summary` (already covered)
- `catalog plan --entry task-confirm-current --view summary`

The `task-buy` boundary should mirror `task-sell`: order input kind, required `port/code/price/quantity`, non-executing mode, and explicit live-trade requirement. The `task-confirm-current` boundary should identify confirmation input kind with no required order fields.

## Registry Boundary

D-07 remains `[部分实现]`. The update only makes existing read-only discovery/planning evidence explicit. It must not imply:

- direct `trade-buy` / `trade-sell` catalog entries are supported
- `catalog run` executes these entries safely
- broker readiness or safety approval is proven
- desktop exception/result dialog coverage is complete

## Test Strategy

Add API CLI tests for `task-buy` and `task-confirm-current` summary projections. Add a FUNCTION_TREE registry test that fails until D-07 names the three task plan entries and keeps the non-execution boundary.
