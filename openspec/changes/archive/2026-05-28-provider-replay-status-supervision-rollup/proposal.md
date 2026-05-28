# provider replay status supervision rollup

## Why

Provider replay status now exposes detailed `lifecycle.supervision_summary`, but the compact `status_summary` still only surfaces ownership/control/operation fields. Operators using `provider-replay status --view summary` need the one-line summary to make the same boundary clear: replay is not supervised, unmanaged, and not observing a tracked process.

This change adds read-only supervision rollup fields to `summary_view.status_summary` without implementing any daemon lifecycle behavior.

## What Changes

- Add compact supervision fields to `provider-replay status --view summary`:
  - `lifecycle_supervision_status`
  - `lifecycle_supervisor_configured`
  - `lifecycle_desired_state`
  - `lifecycle_observed_state`
  - `lifecycle_process_identity_status`
- Derive the fields from existing `lifecycle.supervision_summary`.
- Keep the detailed `status` payload and nested `summary_view.lifecycle.supervision_summary` unchanged.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
