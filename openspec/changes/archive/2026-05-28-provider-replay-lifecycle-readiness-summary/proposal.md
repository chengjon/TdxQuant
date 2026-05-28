# provider replay lifecycle readiness summary

## Why

E-06 now exposes lifecycle status, statefile checks, and non-executing lifecycle plans. Operators still need one read-only place to answer: "is this replay provider ready for lifecycle control, and if not, which requirements are missing?" Without that explicit readiness boundary, valid statefile diagnostics can be misread as permission to control a daemon.

This change adds a non-executing lifecycle readiness summary that keeps `ready=false` and lists missing control requirements until real lifecycle management is implemented.

## What Changes

- Add `provider-replay lifecycle-readiness --config <path>`.
- Optionally include statefile diagnostics with `--include-statefile-check --stale-after-seconds`.
- Return detailed readiness fields:
  - `ready=false`
  - `readiness_status=blocked`
  - `control_allowed=false`
  - `missing_requirements`
  - requirement counts
  - lifecycle/status/statefile summary fields
- Add `--view summary` for compact output.
- Keep all behavior read-only and non-executing.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
