## Why

`catalog validate` now exposes submit-once and PingAn bundle label and step-source distributions, but those subset views still do not show the resolved step-name mix such as `audit`, `trade`, `confirm`, or `success`. Operators can see samples and source classes, but not the step-role composition without inspecting full bundle definitions.

Adding subset step-name counts keeps the validation result compact and non-executing while improving the single `FUNCTION_TREE.md` registry evidence for E-11.

## What Changes

- Add `submit_once_bundle_step_name_counts` to catalog validation output and summary view.
- Add `pingan_bundle_step_name_counts` to catalog validation output and summary view.
- Derive both fields from resolved bundle step `name` values for the existing submit-once and PingAn subset classifications.
- Preserve non-execution behavior: validation still parses static runtime catalog/bundle JSON and does not run entries, bundle steps, reports, tasks, or trades.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
