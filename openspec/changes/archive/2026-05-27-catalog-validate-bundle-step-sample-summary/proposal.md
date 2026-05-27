# catalog validate bundle-step sample summary

## Why

`catalog validate --view summary` already exposes compact bundle step counts and family-specific bounded sample metadata for task/report, submit-once, and PingAn bundle subsets. The generic `bundle_step_summary` does not include equivalent bounded sample metadata, so consumers that validate a selected bundle label need to combine the compact object with sibling fields or family-specific summaries to understand whether visible samples are complete.

Adding bounded sample metadata to `bundle_step_summary` keeps E-11 catalog registration evidence compact while preserving the existing boundary: the command validates and summarizes catalog structure only. It must not execute entries, task/report commands, trade commands, bundle steps, provider calls, or workflow actions.

## What Changes

- Add read-only `bundle_samples`, `bundle_sample_count`, `bundle_sample_limit`, and `bundle_sample_truncated` to bundle validation summary views.
- Add matching `sample_count`, `sample_limit`, and `sample_truncated` fields to the compact `bundle_step_summary` object.
- Derive the new fields from the resolved bundle names selected by existing `catalog validate` filters.
- Preserve existing counts, key-count maps, and family-specific summaries.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
