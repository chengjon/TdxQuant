## Why

Command catalog validation summary views already expose task+report bundle counts, bounded bundle samples, and several task/report step count maps. Consumers that only need compact readiness-adjacent metadata currently have to read many sibling fields.

Adding `task_report_bundle_summary` keeps E-11 evidence compact and explicit while preserving the non-execution catalog boundary: the object summarizes existing validation metadata only and does not execute catalog entries, tasks, reports, trades, or bundle steps.

## What Changes

- Add read-only `task_report_bundle_summary` to `catalog validate --view summary`.
- Derive the object from existing task/report bundle metadata:
  - bundle count
  - step count
  - bounded sample count/limit/truncated state
  - label and step-map key counts
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-11 evidence and boundary text.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-command-catalog`
- Verification: focused pytest for API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
