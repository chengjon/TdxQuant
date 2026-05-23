## Why

D-08 now has a dedicated Ping An `sell_submit_once` manager and task identity, but runtime report/catalog presets still only register the older `buy_submit_once` submit-once audit views. Readers can see the method in code, yet cannot discover matching audit diagnostics through the command catalog.

This change registers a narrow set of `sell_submit_once` audit presets and bundles so the feature tree can state exactly what is discoverable without implying any new trading execution behavior.

## What Changes

- Add daily/period Ping An `sell_submit_once` trade-audit report presets for exceptions, rejected, and failed statuses.
- Add command-catalog entries for those report presets.
- Add diagnostic/follow-up bundles for `sell_submit_once`, including task step options that force `side=sell`.
- Include `side` in catalog plan key fields so planned sell-submit-once bundles do not look like default buy submit-once flows.
- Update `FUNCTION_TREE.md` D-08/E-11 evidence and boundary.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-report-cli-entry`: runtime report preset registry includes Ping An `sell_submit_once` audit views.
- `tdx-command-catalog`: catalog and bundle registry exposes Ping An `sell_submit_once` diagnostics and follow-up bundles.

## Impact

- Affected runtime config: `runtime/report-presets.json`, `runtime/command-catalog.json`, `runtime/command-bundles.json`.
- Affected code: `tdxquant/cli.py`.
- Affected tests: `tests/test_api_manager.py`, `tests/test_api_cli.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
