# provider replay lifecycle ownership summary

## Why

The E-06 daemon lifecycle design now requires future lifecycle status to distinguish configured replay capability, owned daemon process state, observed HTTP health, and stale or missing ownership metadata. The current provider-replay status payload only states that lifecycle management is not provided; it does not expose a stable ownership slot for future lifecycle control.

Adding a read-only `lifecycle.ownership_summary` gives the status payload and summary view a clear place to report the current "not managed / no ownership" state without implementing start, stop, restart, pidfiles, statefiles, or backoff.

## What Changes

- Add read-only `lifecycle.ownership_summary` to provider-replay detailed status.
- Project the same object into `provider-replay status --view summary` under `summary_view.lifecycle.ownership_summary`.
- Current values explicitly report:
  - lifecycle ownership is not managed
  - no owned process is known
  - no lifecycle state file is present or read
  - lifecycle control is not allowed
  - the status source is the configured boundary, not daemon ownership proof
- Keep all existing lifecycle fields and probe/status behavior unchanged.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

