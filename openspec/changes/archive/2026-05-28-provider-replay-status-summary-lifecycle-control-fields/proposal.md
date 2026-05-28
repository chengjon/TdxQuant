# provider replay status summary lifecycle control fields

## Why

`provider-replay status --view summary` now exposes detailed lifecycle ownership and control summaries under `summary_view.lifecycle`, but the compact first-screen `status_summary` still only shows `control_supported` and `managed_operation_count`. Callers that only read `status_summary` cannot see why lifecycle control is blocked or whether any owned process exists.

Adding a few read-only lifecycle fields to `status_summary` keeps the summary self-explanatory without adding lifecycle commands or process control.

## What Changes

- Add read-only lifecycle fields to `summary_view.status_summary`:
  - `lifecycle_ownership_status`
  - `lifecycle_owned_process`
  - `lifecycle_control_status`
  - `lifecycle_blocking_reason`
- Derive them from existing `lifecycle.ownership_summary` and `lifecycle.control_summary`.
- Keep detailed `status`, `summary_view.lifecycle`, probes, and control behavior unchanged.
- Update focused CLI tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

