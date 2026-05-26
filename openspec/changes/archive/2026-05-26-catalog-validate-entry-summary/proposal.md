## Why

Catalog validation summary views expose selected entry counts plus entry source and label count maps. Consumers that only need compact selected-entry metadata currently have to read several sibling fields.

Adding `entry_summary` keeps E-11 evidence compact and explicit while preserving the catalog validation boundary: it summarizes existing selected-entry metadata only and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## What Changes

- Add read-only `entry_summary` to `catalog validate --view summary`.
- Derive the object from existing selected-entry metadata:
  - entry count
  - source key count
  - label key count
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
