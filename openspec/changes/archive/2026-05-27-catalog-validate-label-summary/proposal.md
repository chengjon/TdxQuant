# catalog validate label summary

## Why

`catalog validate --view summary` already exposes entry and bundle label count maps plus key-count siblings. Consumers that only need a compact label-oriented registry view still need to read multiple sibling fields and reconstruct selected-label coverage themselves.

Adding `label_summary` gives E-11 a stable read-only label rollup for catalog discovery and validation while preserving the existing boundary: it summarizes already projected catalog metadata only and must not execute catalog entries, tasks, reports, trades, provider calls, or bundle steps.

## What Changes

- Add read-only `label_summary` to `catalog validate --view summary`.
- Derive the object from existing `selected_label`, `entry_label_counts`, `entry_label_key_count`, `bundle_label_counts`, and `bundle_label_key_count` fields.
- Include selected-label entry/bundle counts and a total distinct label key count across projected entry/bundle label maps.
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
