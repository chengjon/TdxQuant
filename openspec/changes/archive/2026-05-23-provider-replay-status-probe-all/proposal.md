## Why

E-06 now has separate opt-in probes for replay health, watch status, watch events, and watch event-stream. Operators who want the full read-only surface check must pass four flags every time.

Adding a single `--probe-all` convenience flag improves operator ergonomics while preserving the existing boundary: status does not start, stop, restart, daemonize, schedule, or supervise the replay service.

## What Changes

- Add `--probe-all` to `provider-replay status`.
- Treat `--probe-all` as enabling the existing health, watch-status, watch-events, and watch-stream probes.
- Preserve the current individual probe flags and timeout behavior.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary.

## Capabilities

### New Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`: expose a convenience status flag for all existing read-only provider replay probes.

## Impact

- CLI: `tdxquant/cli.py`
- Tests: `tests/test_api_cli.py`
- Registry: `FUNCTION_TREE.md`
- Specs: `openspec/specs/tdx-provider-transport-replay-service/spec.md`
