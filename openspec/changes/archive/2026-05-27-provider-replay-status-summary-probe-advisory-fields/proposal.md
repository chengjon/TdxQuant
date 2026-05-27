# provider replay status summary probe advisory fields

## Why

`provider-replay status --view summary` already includes a compact `status_summary`, but probe posture still requires callers to open the nested `probe_summary`. Now that `probe_summary.advisory_summary` exists, the summary view can surface a few stable read-only probe advisory fields in the first-level `status_summary` without changing probe execution.

This keeps E-06 useful for discovery/status dashboards while preserving the fake-provider boundary: the command remains read-only, opt-in probes stay opt-in, and no daemon lifecycle controls are introduced.

## What Changes

- Add read-only probe advisory fields to `summary_view.status_summary`:
  - `probe_status`
  - `probe_request_coverage_status`
  - `has_problem_probe`
  - `primary_problem_probe`
- Derive those fields from existing `runtime.probe_summary.advisory_summary` with sibling-field fallback for compatibility.
- Keep detailed `status`, copied `probe_summary`, and lifecycle/capability summary fields unchanged.
- Update focused CLI tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

