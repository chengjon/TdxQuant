## Why

`catalog validate` now exposes submit-once and PingAn bundle label distributions, but those subset views still do not show whether their resolved steps are backed by task entries, report entries, or another catalog source. Operators can see samples, but not the structural composition of the subset without inspecting the full bundle definitions.

Adding subset step-source counts keeps the validation result compact and non-executing while improving the single FUNCTION_TREE registry evidence for E-11.

## What Changes

- Add `submit_once_bundle_step_source_counts` to catalog validation output and summary view.
- Add `pingan_bundle_step_source_counts` to catalog validation output and summary view.
- Derive both fields from resolved bundle step `source` values for the existing submit-once and PingAn subset classifications.
- Preserve non-execution behavior: validation still parses static runtime catalog/bundle JSON and does not run entries, bundle steps, reports, tasks, or trades.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
