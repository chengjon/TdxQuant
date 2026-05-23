## Why

D-08 already supports `trade-submit-once` with `side=buy/sell`, and `task-sell-submit-once` has an explicit side-scoped catalog entry. The buy side still depends on the historical default `submit-once-default`, which makes the side boundary less visible in the registry and catalog.

Adding an explicit buy submit-once task entry makes the existing buy path discoverable without adding a new desktop execution primitive.

## What Changes

- Add `buy-submit-once-default` as a task preset that sets `side=buy`.
- Add `task-buy-submit-once` as a command catalog task entry.
- Add buy-scoped PingAn submit-once follow-up bundles that resolve through the explicit buy task entry and existing buy submit-once audit report entries.
- Update `FUNCTION_TREE.md` D-08/E-11 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-command-catalog`: expose explicit buy submit-once task entry and buy-scoped follow-up bundles through the existing catalog planner.

## Impact

- Runtime config: `runtime/task-presets.json`, `runtime/command-catalog.json`, `runtime/command-bundles.json`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-command-catalog/spec.md`
