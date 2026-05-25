## Why

`catalog validate` already reports selected bundle step source/name/entry counts, but it does not expose which option keys are carried by fixed bundle steps. A compact option-key rollup helps review preset surface area without executing tasks, reports, trades, or bundle steps.

## What Changes

- Add `bundle_step_option_key_counts` to detailed `catalog validate` results.
- Add `task_report_bundle_step_option_key_counts` for the task+report bundle subset.
- Mirror both count maps through `catalog validate --view summary`.
- Keep the fields read-only and derived from resolved fixed runtime catalog bundles only.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 evidence and boundary
