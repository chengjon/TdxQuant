## Why

`catalog validate` already exposes count and bounded samples for submit-once and PingAn bundle subsets. Operators can confirm that those fixed runtime bundles exist, but the summary does not show their label distribution without inspecting full bundle definitions.

Adding label-count rollups for these two subsets makes the non-executing registry view more useful while keeping `FUNCTION_TREE.md` clear that these are catalog structure checks, not execution readiness.

## What Changes

- Add `submit_once_bundle_label_counts` to catalog validation output and summary view.
- Add `pingan_bundle_label_counts` to catalog validation output and summary view.
- Derive both fields from selected resolved bundle labels using the existing submit-once and PingAn subset classification.
- Preserve non-execution behavior: validation still parses static runtime catalog/bundle JSON and does not run entries, bundle steps, reports, tasks, or trades.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
