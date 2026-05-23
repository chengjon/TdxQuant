## Why

D-08 now has explicit sell submit-once manager identity, but the command catalog still exposes sell submit-once follow-up bundles by applying `side=sell` as a bundle-step override on the generic `task-submit-once` entry. A dedicated sell-side preset and catalog entry makes the side boundary visible before bundle expansion, reducing the chance that readers infer the default buy path is being used.

## What Changes

- Add a `sell-submit-once-default` task preset targeting the existing `trade-submit-once` task command with `side=sell`.
- Add a `task-sell-submit-once` command catalog entry mapped to that preset.
- Update existing Ping An sell submit-once follow-up bundles to use the explicit sell-side catalog entry.
- Keep the execution path unchanged: the task still calls `trade_submit_once(side="sell")`, and no dedicated `run_pingan_sell_submit_once` desktop primitive is introduced.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-management`: expose an explicit sell-side submit-once task preset that preserves the existing task workflow and safety requirements.
- `tdx-command-catalog`: expose a side-explicit sell submit-once task entry and use it in sell submit-once follow-up bundles.

## Impact

- `runtime/task-presets.json`
- `runtime/command-catalog.json`
- `runtime/command-bundles.json`
- `tests/test_api_cli.py`
- `FUNCTION_TREE.md`
