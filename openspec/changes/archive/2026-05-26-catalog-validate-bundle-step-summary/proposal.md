## Why

Catalog validation summary views expose selected bundle step counts and several step count maps, but consumers that only need compact selected-bundle metadata must read many sibling fields.

Adding `bundle_step_summary` keeps E-11 evidence compact and explicit while preserving the catalog validation boundary: it summarizes existing selected-bundle metadata only and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## What Changes

- Add read-only `bundle_step_summary` to `catalog validate --view summary`.
- Derive the object from existing selected bundle metadata:
  - bundle count
  - bundle step count
  - label key count
  - selected step source/name/entry/source-name/source-entry/option-key/source-option-key map key counts
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
