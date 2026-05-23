## Why

The ordinary sell path already has PingAn exception, rejection, and failure follow-up bundles, but it lacks the success-oriented complete-review alias that ordinary buy and confirm_current now expose. This leaves PingAn sell success review less discoverable through the catalog.

Adding `sell-pingan-complete-review` keeps the ordinary buy/sell PingAn catalog naming symmetric without introducing a new execution primitive.

## What Changes

- Add `sell-pingan-complete-review` to `runtime/command-bundles.json`.
- Route the bundle through existing `task-sell`, `daily-success`, and `audit-daily-pingan-confirmed` entries.
- Keep existing `sell-pingan-exception-review`, `sell-pingan-rejection-review`, and `sell-pingan-failure-review` bundles unchanged.
- Update `FUNCTION_TREE.md` D-07/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose an ordinary sell PingAn complete-review bundle through the existing catalog planner.

## Impact

- Runtime config: `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
