# provider replay lifecycle control summary

## Why

Provider replay now exposes a read-only lifecycle ownership summary that says the current status surface does not own any daemon process. The next useful boundary is to make lifecycle control availability equally explicit: start, stop, restart, and backoff are designed/pending, not currently supported operations.

Adding `lifecycle.control_summary` gives clients a stable read-only place to understand that lifecycle controls are blocked and why, without adding any control command or process mutation.

## What Changes

- Add read-only `lifecycle.control_summary` to provider-replay detailed status.
- Project the same object into `provider-replay status --view summary` under `summary_view.lifecycle.control_summary`.
- Current values explicitly report:
  - lifecycle control is unsupported
  - available operations are empty
  - blocked operations are `start`, `stop`, `restart`, and `backoff`
  - blocking reason is lifecycle control not implemented
  - ownership proof is required before future stop/restart control
- Keep all status/probe/summary behavior read-only.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

