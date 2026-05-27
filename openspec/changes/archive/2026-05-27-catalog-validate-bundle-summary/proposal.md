# catalog validate bundle summary

## Why

`catalog validate --view summary` now exposes bundle counts, bounded bundle samples, label summaries, source summaries, and step-oriented rollups. Consumers that need a compact bundle-oriented registry view still have to read several sibling fields and reconstruct whether a bundle selection exists, how many bundle samples are visible, and how many resolved steps are represented.

Adding `bundle_summary` gives E-11 a stable read-only bundle rollup for catalog discovery and validation while preserving the existing boundary: it summarizes already projected catalog metadata only and must not execute catalog entries, tasks, reports, trades, provider calls, or bundle steps.

## What Changes

- Add read-only `bundle_summary` to `catalog validate --view summary`.
- Derive the object from existing `selected_bundle`, `selected_label`, `bundle_count`, `bundle_step_count`, bounded bundle sample metadata, and bundle label key-count fields.
- Include booleans for whether the selected validation view has bundles and whether the bounded sample is truncated.
- Preserve existing sibling fields and `bundle_step_summary` for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
