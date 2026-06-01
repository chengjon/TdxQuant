## Why

D-13 exposes PingAn trade execution acceptance evidence through the trade manager and CLI, but automation cannot yet discover or plan that entry through the command catalog. Adding a catalog entry keeps the acceptance evidence surface visible in the same non-executing registry used by other PingAn trade diagnostics.

## What Changes

- Add a trade preset for `acceptance-evidence`.
- Add a command catalog entry for the preset with PingAn/acceptance/read-only labels.
- Ensure catalog plan/summary can expose the entry as a non-executing trade plan boundary.
- Register the catalog discoverability evidence in `FUNCTION_TREE.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-command-catalog`: registers and plans the PingAn trade acceptance evidence entry without execution.
- `tdx-function-tree-registry`: records the D-13 catalog discoverability evidence and boundary.

## Impact

- Affected data: `runtime/trade-presets.json`, `runtime/command-catalog.json`.
- Affected code/tests: catalog plan boundary handling if needed, `tests/test_api_cli.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, OpenSpec delta specs.
- No trade, broker, desktop, task, report, bundle, or status-transition execution is introduced.
