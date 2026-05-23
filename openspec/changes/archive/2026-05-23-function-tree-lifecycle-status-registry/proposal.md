# Close FUNCTION_TREE Lifecycle Material Registry Status

## Why

A-08 tracks the OpenSpec lifecycle material and FUNCTION_TREE registry validation surface. After adding OpenSpec evidence validation, local evidence path validation, ROADMAP rejection, and JSON report output, the lifecycle registry tooling now has source, tests, archived specs, and an explicit boundary.

The current `[部分实现]` status understates the registry validation tooling itself, while the boundary already prevents readers from treating the validator as proof that every cited feature is runnable.

## What Changes

- Reclassify A-08 from `[部分实现]` to `[已实现]`.
- Keep the boundary explicit: lifecycle material validates registry structure and evidence references only; it does not execute evidence or prove feature availability.
- Add this OpenSpec change id as status-transition evidence.

## Impact

- Affected registry: `FUNCTION_TREE.md`
- Affected spec: `tdx-function-tree-registry`
- Tests: existing FUNCTION_TREE validator tests and validator script runs
- Boundary: no runtime feature semantics change.
