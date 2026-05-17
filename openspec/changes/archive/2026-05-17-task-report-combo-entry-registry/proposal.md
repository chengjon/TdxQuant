# task-report-combo-entry-registry

## Why

`FUNCTION_TREE.md` is the single feature registry. E-11 still marks "more task/report combo entries" as designed/not implemented even though the runtime catalog already contains concrete task/report follow-up bundles and the CLI can list and plan them without executing side effects.

This change closes that registry gap by making the task/report combo evidence explicit, tested, and bounded. It does not introduce a new workflow engine or expand underlying trading/reporting semantics.

## What Changes

- Add an OpenSpec contract that the command catalog exposes discoverable task/report combo bundles for daily follow-up workflows.
- Add focused CLI tests proving a task/report combo bundle is discoverable and plans to task plus report steps without execution.
- Update `FUNCTION_TREE.md` E-11 from designed/not implemented to partial implementation with concrete evidence and a boundary.
- Update the historical project function map wording so it defers combo-entry truth to `FUNCTION_TREE.md`.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Runtime behavior: no semantic change to `catalog run`, task execution, report generation, or bundle dispatch.
- Config: uses existing runtime catalog/bundle entries as evidence.
- Tests: focused CLI/catalog tests only.
- Documentation: `FUNCTION_TREE.md` remains the single feature registry.
