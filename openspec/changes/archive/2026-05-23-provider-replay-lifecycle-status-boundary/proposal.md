## Why

`FUNCTION_TREE.md` keeps E-06 as a partial daemon fake-provider node because the replay HTTP service can project read-only fake-provider data, but it does not manage daemon lifecycle. Callers need a machine-readable status surface that makes that boundary explicit instead of inferring daemon capability from the existing `serve` command.

## What Changes

- Add a replay-provider status summary that reports configured provider identity, listen settings, replay source selection, read-only endpoint coverage, and lifecycle boundary metadata.
- Expose the summary through a `provider-replay status --config <path>` CLI command that loads config without opening a socket.
- Keep `provider-replay serve` foreground-only and explicitly out of daemon start/stop management.
- Update `FUNCTION_TREE.md` E-06 evidence and boundary without promoting the node to fully implemented.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`: add lifecycle/status boundary reporting for the replay fake-provider surface.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`.
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`.
- Documentation: `FUNCTION_TREE.md`.
- Dependencies: none.
