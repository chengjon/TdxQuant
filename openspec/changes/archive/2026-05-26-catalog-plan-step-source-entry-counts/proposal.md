# Add catalog plan step source-entry counts

## Why

`catalog plan|preview --bundle ... --view summary` now exposes selected-step source, name, entry, and `source:name` distributions. The remaining compact fingerprint that callers need for bundle composition review is `source:entry`: it identifies which dispatch source owns each selected entry without requiring the fuller selected step projection.

Adding source-qualified step entry counts keeps the summary view useful for review and catalog QA while preserving the existing boundary: no option values, no resolved arguments, no full manifest, and no step execution.

## What Changes

- Add `step_source_entry_counts` to bundle plan/preview summary views.
- Add `step_source_entry_key_count` equal to `len(step_source_entry_counts)`.
- Derive both fields only from selected resolved bundle steps' string `source` and `entry` fields.
- Keep existing `selected_step_count`, `step_source_counts`, `step_name_counts`, `step_entry_counts`, and `step_source_name_counts` semantics unchanged.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
- Registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]` with explicit evidence and non-execution boundary.
