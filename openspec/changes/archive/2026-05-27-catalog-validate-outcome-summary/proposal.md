## Why

`catalog validate --view summary` exposes many entry, bundle, and combo counts, but callers that only need to know the validation outcome still have to combine `valid`, `invalid_count`, `non_execution`, and selected target counts themselves. A compact outcome object makes the summary view easier to consume without changing its non-executing boundary.

## What Changes

- Add an additive `validation_outcome` object to catalog validation summary views.
- Derive the object from existing summary fields: kind, selected label, entry/bundle counts, invalid count, validity, result code/message, and non-execution flag.
- Keep it read-only and non-executing: it must not run catalog entries, bundles, task/report steps, trade commands, or workflow actions.

## Impact

- Affected spec: `tdx-command-catalog`
- Affected code: catalog summary projection, focused CLI tests, and `FUNCTION_TREE.md` E-11 registry evidence/boundary.
