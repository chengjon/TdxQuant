## Why

Provider replay status already exposes aggregate probe status counts and aggregate `error_code_counts`. Operators can see all probe error codes, but cannot directly distinguish which error codes belong to the failed/unhealthy requested probe set without inspecting individual probe payloads.

Adding failed-only error-code counts keeps the summary compact and aligned with the existing `failed` / `failed_status_counts` boundary.

## What Changes

- Add `runtime.probe_summary.failed_error_code_counts` to provider replay status.
- Count only requested probes that are not `healthy` and have a string `error_code`.
- Preserve existing probe execution, endpoint selection, summary view projection, foreground-only status behavior, and no-daemon-lifecycle boundary.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected CLI behavior: `provider-replay status --view summary` includes the additive field through the existing full `probe_summary` projection
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused provider replay and CLI tests plus OpenSpec and FUNCTION_TREE registry validation
