# Design

## Context

The catalog layer already composes existing `task`, `report`, and `trade` presets through `runtime/command-catalog.json` and `runtime/command-bundles.json`. That composition is intentionally thin: a bundle step resolves to an existing catalog entry and dispatches through the original command group.

E-11 is not asking for a new execution model. The remaining gap is that the single feature registry still says the task/report combo work is designed/not implemented, while concrete runtime bundles such as `confirm-complete-review` exist and are plan-able through the CLI.

## Goals

- Treat task/report combo entries as partially implemented only when there is runtime config, CLI exposure, and test coverage.
- Keep `FUNCTION_TREE.md` as the authoritative status register.
- Make the boundary explicit: these are named preset compositions, not arbitrary user-defined workflow automation.

## Non-Goals

- Do not add new trading, reporting, or audit aggregation semantics.
- Do not change `runtime/command-bundles.json` schema.
- Do not make catalog metadata the source of truth for overall feature availability.
- Do not mark all possible task/report combinations as implemented.

## Decisions

### 1. Use existing concrete bundles as evidence

`runtime/command-bundles.json` already contains named bundles that combine task-source steps with report-source steps. The change validates those bundles instead of adding another near-duplicate entry only to satisfy the registry.

### 2. Test discovery and planning, not execution

The focused tests use `catalog list` and `catalog plan` because those paths prove CLI exposure and argument resolution without requiring live desktop trading or report artifacts.

### 3. Registry wording must stay bounded

E-11 moves to `[部分实现]`, not `[已实现]`, because this closes a set of stable named combos, not every future task/report/catalog composition.

## Risks / Trade-offs

- Registry drift can reappear if future catalog bundles are added without evidence updates. The added test reduces that risk for the current representative combo surface.
- Reusing existing bundles keeps runtime behavior stable, but it means this change is mostly contract and registry hardening rather than feature expansion.
