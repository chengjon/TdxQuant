## Why

`task-buy-submit-once` now gives the buy side an explicit catalog entry, but the success/confirmed follow-up path still uses the older generic `task-submit-once` bundle. That leaves the happy-path PingAn buy submit-once review less explicit than the exception/rejection/failure follow-ups.

Adding a buy-scoped complete-review bundle keeps catalog discovery consistent without changing trade execution behavior.

## What Changes

- Add `buy-submit-once-pingan-complete-review` to `runtime/command-bundles.json`.
- Route the bundle trade step through `task-buy-submit-once`.
- Reuse existing `daily-success` and PingAn confirmed trade-audit report entries.
- Update `FUNCTION_TREE.md` D-08/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose a buy-scoped PingAn submit-once complete-review bundle through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
