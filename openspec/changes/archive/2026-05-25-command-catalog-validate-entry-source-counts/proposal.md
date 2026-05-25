## Why

`catalog validate` reports entry counts and entry label counts, but it does not expose which catalog sources those selected entries resolve to. A compact source count map helps audit fixed entry coverage across report/task/trade surfaces without executing entries.

## What Changes

- Add `entry_source_counts` to detailed `catalog validate` results.
- Mirror `entry_source_counts` through `catalog validate --view summary`.
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
