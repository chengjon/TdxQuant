## Why

`catalog plan --view summary` exposes top-level selected step `source:name` and `source:entry` key counts, but `selected_step_summary` does not include those pair-key counts. Callers that consume the selected-step rollup have to read sibling top-level fields to understand whether the selected slice has mixed source/name or source/entry shapes.

## What Changes

- Add additive `selected_step_summary.step_source_name_key_count` and `selected_step_summary.step_source_entry_key_count`.
- Derive both fields from existing selected bundle plan summary metadata.
- Keep the fields read-only and non-executing: no catalog entry, bundle, task, report, trade, provider, or workflow execution.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog selected-step summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
