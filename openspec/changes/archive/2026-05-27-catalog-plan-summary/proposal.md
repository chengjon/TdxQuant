# catalog plan summary

## Why

`catalog plan|preview --view summary` already exposes `plan_outcome` and `selected_step_summary`. Consumers that need a single read-only planning registry object still need to combine those siblings to understand the selected target, non-execution status, selected step count, step slice, and distinct source/name/entry/argument key counts.

Adding `plan_summary` gives E-11 a stable top-level planning summary for catalog discovery and registration while preserving the existing boundary: it summarizes already projected plan metadata only and must not execute catalog entries, tasks, reports, trades, provider calls, or bundle steps.

## What Changes

- Add read-only `plan_summary` to `catalog plan|preview --view summary`.
- Derive the object from existing `plan_outcome`, `selected_step_summary`, and sibling selected-step count fields.
- Include target identity, execution mode, non-execution marker, selected step range, step count, key counts, and high-level presence flags.
- Preserve existing sibling fields and compact summary objects for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
