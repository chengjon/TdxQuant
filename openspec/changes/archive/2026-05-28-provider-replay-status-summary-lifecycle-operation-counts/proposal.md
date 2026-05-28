# provider replay status summary lifecycle operation counts

## Why

`provider-replay status --view summary` now exposes detailed per-operation lifecycle status under `summary_view.lifecycle.operation_summary`. The compact first-screen `status_summary` still lacks operation counts, so callers must open the nested lifecycle object to see whether any lifecycle operation is available.

Adding read-only lifecycle operation count fields to `status_summary` makes the current blocked operation posture visible at a glance without adding lifecycle control behavior.

## What Changes

- Add read-only lifecycle operation count fields to `summary_view.status_summary`:
  - `lifecycle_operation_count`
  - `lifecycle_available_operation_count`
  - `lifecycle_blocked_operation_count`
  - `lifecycle_primary_blocked_operation`
- Derive them from existing `lifecycle.operation_summary`.
- Keep detailed `status`, `summary_view.lifecycle`, probes, and control behavior unchanged.
- Update focused CLI tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

