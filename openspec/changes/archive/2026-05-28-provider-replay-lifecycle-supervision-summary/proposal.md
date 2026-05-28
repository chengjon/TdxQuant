# provider replay lifecycle supervision summary

## Why

E-06 is still a partial daemon lifecycle node: provider replay can describe its foreground/read-only boundary, but it cannot be started, stopped, supervised, or recovered as a managed daemon. Recent lifecycle slices added ownership, control, operation, and backoff summaries. The remaining ambiguity is whether any supervisor or process tracking exists behind those fields.

Adding `lifecycle.supervision_summary` makes the current "not supervised / not tracked" state explicit without implementing lifecycle control.

## What Changes

- Add read-only `lifecycle.supervision_summary` to provider-replay detailed status.
- Project the same object into `provider-replay status --view summary` under `summary_view.lifecycle.supervision_summary`.
- Current values explicitly report:
  - no supervisor is configured
  - no managed process or pid/state tracking exists
  - desired state and observed state are unmanaged/not observed
  - lifecycle control remains blocked because it is not implemented
- Keep all existing provider replay status, probe, and summary behavior read-only.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`, `tdxquant/cli.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
