# provider replay lifecycle statefile check

## Why

E-06 now has a configured statefile boundary and non-executing lifecycle plans, but it still cannot explicitly validate a future lifecycle statefile shape. A separate read-only check command lets operators and tests inspect a configured statefile intentionally without changing the behavior of `status`, `config-check`, or `lifecycle-plan`.

This change adds an opt-in statefile schema/staleness check. It reads only the configured file when the caller invokes the check command, never writes it, and never uses it to authorize lifecycle control.

## What Changes

- Add `provider-replay lifecycle-state-check --config <path>`.
- Read the configured `lifecycle_state_file` only for this explicit check command.
- Validate a minimal lifecycle statefile shape:
  - `schema_version`
  - `provider_id`
  - `pid`
  - `state`
  - `updated_at`
- Report provider-id match and stale status using `--stale-after-seconds`.
- Add `--view summary` for compact output.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
