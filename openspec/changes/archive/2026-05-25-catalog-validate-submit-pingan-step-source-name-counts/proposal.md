## Why

`catalog validate` now exposes submit-once and PingAn bundle label, step-source, and step-name distributions. The remaining compact view gap is the paired `source:name` shape that distinguishes, for example, `task:trade` from `report:success` without requiring callers to inspect full bundle definitions.

Adding subset source-name counts improves E-11 registry evidence while keeping catalog validation non-executing and bounded.

## What Changes

- Add `submit_once_bundle_step_source_name_counts` to catalog validation output and summary view.
- Add `pingan_bundle_step_source_name_counts` to catalog validation output and summary view.
- Derive both fields from resolved bundle step `source` and `name` values for the existing submit-once and PingAn subset classifications.
- Preserve non-execution behavior: validation still parses static runtime catalog/bundle JSON and does not run entries, bundle steps, reports, tasks, or trades.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
