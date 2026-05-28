# provider replay lifecycle statefile boundary

## Why

E-06 remains partial because provider replay exposes lifecycle status but still has no managed daemon ownership model. A future daemon controller will need an explicit statefile contract before it can safely reason about owned processes, stale state, or control operations. Today there is no stable config/status slot for that boundary.

This change adds a read-only `lifecycle_state_file` configuration slot and reports that the statefile is configured or absent without reading, writing, or trusting it for control.

## What Changes

- Add optional `lifecycle_state_file` parsing to `ProviderTransportReplayConfig`.
- Add read-only `lifecycle.statefile_summary` to provider-replay detailed status.
- Add config-check summary fields showing whether a lifecycle statefile path was provided and that config-check does not inspect or write it.
- Keep current status and config-check behavior non-executing.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
