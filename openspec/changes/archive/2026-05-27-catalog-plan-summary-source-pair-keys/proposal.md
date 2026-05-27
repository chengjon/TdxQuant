## Why

`selected_step_summary` now carries selected step `source:name` and `source:entry` pair-key counts, while `plan_summary` still exposes only source/name/entry single-key counts plus resolved-arg counts. Callers that rely on the compact planning summary need the same pair-key count hints without reading sibling fields.

## What Changes

- Add additive `plan_summary.step_source_name_key_count` and `plan_summary.step_source_entry_key_count`.
- Derive both fields only from the existing `selected_step_summary` pair-key count fields.
- Keep the projection read-only and non-executing: no workflow, task, report, trade, provider, or bundle step execution.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog plan summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
