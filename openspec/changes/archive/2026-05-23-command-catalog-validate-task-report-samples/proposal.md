## Why

`catalog validate --view summary` reports task+report bundle counts, but the compact output does not show any representative bundle ids. E-11 uses `FUNCTION_TREE.md` as the single registry, so a non-executing summary should provide auditable samples without requiring callers to inspect the full detailed runtime JSON.

## What Changes

- Track a small deterministic list of task+report bundle ids during catalog validation.
- Include `task_report_bundle_samples` in the validation payload and opt-in summary view when matching bundles exist.
- Preserve the default detailed behavior and keep validation non-executing.
- Update E-11 in `FUNCTION_TREE.md` with the new evidence and boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-command-catalog`: catalog validation summary includes representative task+report bundle samples.

## Impact

- Catalog validation and summary projection in `tdxquant/cli.py`.
- Catalog validation tests in `tests/test_api_cli.py`.
- `tdx-command-catalog` OpenSpec requirement.
- `FUNCTION_TREE.md` E-11 evidence and boundary text.
