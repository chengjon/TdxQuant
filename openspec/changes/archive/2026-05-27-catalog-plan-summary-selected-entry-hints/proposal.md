## Why

`catalog plan --view summary` now exposes selected step index, name, source, and command hints in `plan_summary`, but the first/last selected catalog entry hints still live only in the sibling `selected_step_summary`. Callers that consume the compact planning summary need a stable way to see which catalog entries bound the selected step range without reading the full step list.

## What Changes

- Add additive `plan_summary.first_step_entry` and `plan_summary.last_step_entry` fields.
- Derive both fields only from the already-built `selected_step_summary` payload.
- Keep the projection read-only and non-executing: no workflow, task, report, trade, provider, or bundle step execution.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
