## Why

`catalog plan --view summary` exposes selected step counts and step composition maps, but callers still need to combine target, constraints, selected step count, and result metadata to understand the plan boundary. A compact plan outcome keeps the non-executing contract explicit.

## What Changes

- Add an additive `plan_outcome` object to catalog plan/preview summary views.
- Derive it from existing summary fields: mode, target, selected step count, step-source key count, result code/message, and non-execution constraints.
- Keep it read-only and non-executing: it must not execute catalog entries, bundles, task/report steps, trade commands, provider calls, or workflow actions.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
