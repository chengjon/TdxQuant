## Why

The ordinary buy path now has a PingAn complete-review alias, but its exception-oriented follow-ups are still only available through the guarded-buy family. That leaves the `task-buy` path less discoverable than the guarded one for PingAn exception, rejection, and failure diagnostics.

Adding ordinary buy PingAn exception/rejection/failure bundles keeps the catalog naming consistent without introducing a new execution primitive.

## What Changes

- Add `buy-pingan-exception-review`, `buy-pingan-rejection-review`, and `buy-pingan-failure-review` to `runtime/command-bundles.json`.
- Route the bundles through existing `task-buy` and PingAn buy audit report entries.
- Keep the existing guarded-buy bundles unchanged.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose ordinary buy PingAn exception/rejection/failure review bundles through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
