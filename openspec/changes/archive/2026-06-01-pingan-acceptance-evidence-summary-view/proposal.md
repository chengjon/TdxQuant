## Why

D-13 is discoverable through the trade CLI and command catalog, but the direct `trade acceptance-evidence` command only returns the detailed payload. CI and automation need a stable, compact summary projection that can be inspected without parsing every detailed category and boundary field.

## What Changes

- Add `--view detailed|summary` to `trade acceptance-evidence`.
- Keep `detailed` as the default behavior.
- For `--view summary`, attach a `summary_view` payload with target nodes, covered trade commands/methods, evidence categories, artifact target keys, and explicit false side-effect flags.
- Register the summary view evidence in `FUNCTION_TREE.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-desktop-trading-cli-entry`: adds a stable summary view for `trade acceptance-evidence`.
- `tdx-function-tree-registry`: registers the D-13 summary view evidence and boundary.

## Impact

- Affected code/tests: `tdxquant/cli.py`, `tests/test_api_cli.py`.
- Affected registry/specs: `FUNCTION_TREE.md`, OpenSpec specs.
- No trade, broker, desktop, task, report, bundle, catalog dispatch, live/manual acceptance evaluation, or status-transition execution is introduced.
