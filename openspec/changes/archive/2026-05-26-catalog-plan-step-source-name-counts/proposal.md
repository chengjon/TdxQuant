# Add catalog plan step source-name counts

## Why

`catalog plan|preview --bundle ... --view summary` already exposes selected-step source, name, and entry distributions for read-only bundle inspection. Callers can see source counts and name counts separately, but cannot tell which names came from which dispatch source without inspecting the fuller selected step projection.

Adding source-qualified step name counts gives the summary view a compact non-executing fingerprint of selected bundle composition while preserving the existing boundary: no option values, no resolved arguments, no full manifest, and no step execution.

## What Changes

- Add `step_source_name_counts` to bundle plan/preview summary views.
- Add `step_source_name_key_count` equal to `len(step_source_name_counts)`.
- Derive both fields only from selected resolved bundle steps' string `source` and `name` fields.
- Keep existing `selected_step_count`, `step_source_counts`, `step_name_counts`, and `step_entry_counts` semantics unchanged.

## Capabilities

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Code: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
- Registry: `FUNCTION_TREE.md` E-11 remains `[部分实现]` with explicit evidence and non-execution boundary.
