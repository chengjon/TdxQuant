# provider replay lifecycle plan statefile diagnostics

## Why

E-06 now has both a read-only lifecycle plan and an explicit lifecycle statefile check. The plan currently only knows whether a statefile path is configured. It does not expose the schema/staleness diagnostic that an operator would need before deciding whether future lifecycle control work is even plausible.

This change adds opt-in statefile diagnostics to `provider-replay lifecycle-plan` while keeping the plan non-executing and control-disallowed.

## What Changes

- Add `--include-statefile-check` and `--stale-after-seconds` to `provider-replay lifecycle-plan`.
- When requested, run the existing read-only statefile check and embed compact diagnostics into the lifecycle plan.
- Add matching summary-view fields.
- Keep default lifecycle-plan behavior unchanged: no statefile read unless explicitly requested.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/cli.py`
- Affected tests: `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for API CLI/provider replay, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
