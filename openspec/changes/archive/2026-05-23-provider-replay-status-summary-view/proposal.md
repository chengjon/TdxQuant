## Why

`provider-replay status` already reports lifecycle boundaries and optional probe rollups, but callers that only need the fake-provider posture must inspect the full detailed payload. A summary view makes the existing boundary and probe status easier to consume without implying daemon lifecycle management.

## What Changes

- Add `provider-replay status --view summary`.
- Keep the default detailed status unchanged.
- Project existing lifecycle, runtime observation, `probe_summary`, and boundaries into a compact summary payload.
- Preserve the explicit boundary that the command does not start, stop, restart, supervise, or observe a live market session.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: add an opt-in CLI summary view for provider replay lifecycle status.

## Impact

- Affected code/tests: `tdxquant/cli.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` node `E-06`
