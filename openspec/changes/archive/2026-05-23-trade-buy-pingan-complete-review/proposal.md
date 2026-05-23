## Why

D-07 has stable ordinary buy task entry (`task-buy`) and guarded-buy PingAn follow-up bundles. The ordinary buy path lacks a PingAn complete-review bundle, so callers who do not want the guarded-buy preset cannot discover a matching happy-path review through the catalog.

Adding `buy-pingan-complete-review` makes the ordinary task-buy path explicit while reusing existing execution and report entries.

## What Changes

- Add `buy-pingan-complete-review` to `runtime/command-bundles.json`.
- Route the bundle through existing `task-buy`, `daily-success`, and `audit-daily-pingan-confirmed` entries.
- Keep existing guarded-buy PingAn bundles unchanged.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose an ordinary task-buy PingAn complete-review bundle through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
