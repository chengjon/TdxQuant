## Why

`provider-replay status --view summary` exposes lifecycle and probe boundaries, but it does not compactly project the read-only capability boundary that is already present in detailed status. E-06 should make fake-provider availability clear without implying daemon lifecycle management or write support.

## What Changes

- Add a compact `capabilities` object to provider replay status summary view.
- Project only bounded fields: `read_only`, `writes_supported`, and `endpoint_count`.
- Keep full endpoint detail in the detailed status payload only.
- Preserve current probe, lifecycle, and config-check behavior.
- Update E-06 in `FUNCTION_TREE.md` with explicit evidence and boundary text.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: status summary view includes read-only capability boundary fields.

## Impact

- Provider replay CLI summary helper in `tdxquant/cli.py`.
- Provider replay CLI tests in `tests/test_api_cli.py`.
- `tdx-provider-transport-replay-service` OpenSpec requirement.
- `FUNCTION_TREE.md` E-06 evidence and boundary text.
