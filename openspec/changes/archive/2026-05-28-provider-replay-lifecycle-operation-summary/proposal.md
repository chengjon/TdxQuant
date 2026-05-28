# provider replay lifecycle operation summary

## Why

Provider replay lifecycle status now says lifecycle control is unsupported and lists blocked operations. That is enough for a coarse boundary, but callers still cannot inspect each operation's current status without hard-coding the blocked operation list.

Adding `lifecycle.operation_summary` gives a stable per-operation read-only matrix for `start`, `stop`, `restart`, and `backoff`. It keeps all current operations blocked while documenting the exact reason and future requirements.

## What Changes

- Add read-only `lifecycle.operation_summary` to provider-replay detailed status.
- Project the same object into `provider-replay status --view summary` under `summary_view.lifecycle.operation_summary`.
- Current operation entries report:
  - operation name
  - `status=blocked`
  - `blocking_reason=lifecycle_control_not_implemented`
  - ownership/operator requirements
  - no current command implementation
- Keep all existing status/probe/summary behavior read-only.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

