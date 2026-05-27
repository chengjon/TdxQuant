## Why

`catalog plan --view summary` already exposes `selected_step_summary`, but callers that only read `plan_summary` still have to dig through a sibling object to recover the selected step range and first/last hint fields. That makes the planning summary less stable as a registry surface than it could be.

## What Changes

- Add additive top-level `plan_summary` hints for the already-derived selected step range metadata.
- Derive the new fields only from the existing `selected_step_summary` payload.
- Keep the data read-only and non-executing: it must not run bundle steps, resolve new arguments, or claim workflow readiness.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
