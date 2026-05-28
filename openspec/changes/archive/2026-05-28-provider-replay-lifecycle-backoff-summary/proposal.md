# provider replay lifecycle backoff summary

## Why

The E-06 daemon lifecycle design says any future supervised backoff policy must be opt-in, bounded, and observable through retry/delay/last-failure/next-retry state. The current provider-replay lifecycle status blocks `backoff`, but it does not expose a dedicated backoff status slot.

Adding `lifecycle.backoff_summary` records the current "not configured / not scheduled" backoff boundary without implementing supervised restart or scheduling.

## What Changes

- Add read-only `lifecycle.backoff_summary` to provider-replay detailed status.
- Project the same object into `provider-replay status --view summary` under `summary_view.lifecycle.backoff_summary`.
- Current values explicitly report:
  - backoff is not configured and disabled
  - retry count is zero
  - no delay window or last failure reason is available
  - next retry is not scheduled or pending
  - the behavior is blocked because lifecycle control is not implemented
- Keep all existing status/probe/summary behavior read-only.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

