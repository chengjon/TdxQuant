## Why

The stable `trade-sell` task command exists, but the daily command catalog still lacks a matching `task-sell` preset entry and ordinary sell follow-up bundles. This makes the feature registry overstate discoverability unless the preset/catalog layer is closed explicitly.

## What Changes

- Add a `task-sell-default` task preset that targets the existing `trade-sell` task command.
- Register a `task-sell` command catalog entry mapped to that preset.
- Add ordinary Ping An sell follow-up bundles that combine `task-sell` with existing sell audit diagnostics.
- Keep catalog planning non-executing and do not add new trading primitives or bypass trade safety controls.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-task-management`: expose a stable `task-sell-default` preset for the existing `trade-sell` task workflow.
- `tdx-command-catalog`: expose the `task-sell` catalog entry and ordinary Ping An sell follow-up bundles.

## Impact

- `runtime/task-presets.json`
- `runtime/command-catalog.json`
- `runtime/command-bundles.json`
- `tests/test_api_cli.py`
- `FUNCTION_TREE.md`
