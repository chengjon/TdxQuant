## Why

The sell submit-once path has PingAn exception, rejection, and failure follow-up bundles, while the buy submit-once path also has a success-oriented complete-review bundle. The missing sell submit-once complete-review alias makes the catalog asymmetric and less discoverable.

Adding `sell-submit-once-pingan-complete-review` keeps the submit-once buy/sell PingAn review naming consistent without changing the underlying execution path.

## What Changes

- Add `sell-submit-once-pingan-complete-review` to `runtime/command-bundles.json`.
- Route the bundle through existing `task-sell-submit-once`, `daily-success`, and `audit-daily-pingan-confirmed` entries.
- Keep existing sell submit-once PingAn exception/rejection/failure bundles unchanged.
- Update `FUNCTION_TREE.md` D-08/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose a sell submit-once PingAn complete-review bundle through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
