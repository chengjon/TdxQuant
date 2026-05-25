## Why

`catalog validate` now exposes submit-once and PingAn subset label, step-source, step-name, and source-name distributions. The next compact registry gap is the concrete step `entry` distribution that shows which static catalog entries appear in those subsets without returning full bundle rows.

Adding subset step-entry counts improves E-11 evidence while preserving non-execution and avoiding any claim of runtime readiness.

## What Changes

- Add `submit_once_bundle_step_entry_counts` to catalog validation output and summary view.
- Add `pingan_bundle_step_entry_counts` to catalog validation output and summary view.
- Derive both fields from resolved bundle step `entry` values for the existing submit-once and PingAn subset classifications.
- Preserve non-execution behavior: validation still parses static runtime catalog/bundle JSON and does not run entries, bundle steps, reports, tasks, or trades.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
