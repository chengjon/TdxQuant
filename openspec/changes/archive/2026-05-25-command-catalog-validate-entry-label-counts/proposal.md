## Why

`catalog validate` reports entry counts and bundle label counts, but it does not expose label coverage for selected catalog entries. A compact entry label rollup lets operators audit fixed entry coverage without listing full entry rows or executing any command.

## What Changes

- Add `entry_label_counts` to detailed `catalog validate` results.
- Mirror `entry_label_counts` through `catalog validate --view summary`.
- Keep the field read-only and derived from resolved fixed catalog entries only.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-command-catalog`

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-11 evidence and boundary
