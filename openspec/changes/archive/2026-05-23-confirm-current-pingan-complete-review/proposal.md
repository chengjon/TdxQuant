## Why

D-07 has stable `confirm_current` task/catalog flow and multiple PingAn follow-up bundles. The generic `confirm-pingan-complete-review` exists, but the `confirm-current-pingan-*` alias family does not include a complete-review alias, so callers cannot discover the happy-path review through the same naming convention.

Adding `confirm-current-pingan-complete-review` keeps the alias family consistent without adding a new desktop execution primitive.

## What Changes

- Add `confirm-current-pingan-complete-review` to `runtime/command-bundles.json`.
- Route it through existing `task-confirm-current`, `daily-success`, and `audit-daily-pingan-confirmed` entries.
- Keep existing `confirm-pingan-complete-review` available.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose a confirm-current PingAn complete-review alias through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
