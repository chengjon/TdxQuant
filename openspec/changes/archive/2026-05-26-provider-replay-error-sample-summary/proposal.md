## Why

Provider replay probe summaries already expose bounded error samples plus separate count, visible-count, hidden-count, limit, truncated, primary sample, status, error-code, HTTP-status, and reachability fields. Consumers that need to understand whether the compact sample projection is complete must read several sibling fields.

Adding `runtime.probe_summary.error_sample_summary` keeps E-06 evidence compact and explicit while preserving the replay-only boundary: it summarizes existing error sample metadata, does not expose full probe payloads, and does not manage daemon lifecycle.

## What Changes

- Add read-only `runtime.probe_summary.error_sample_summary` to provider replay status payloads.
- Derive the object only from existing probe-summary error sample metadata:
  - total/visible/hidden sample counts
  - sample limit and truncated flag
  - primary error sample probe/status/error-code/HTTP-status/reachability
- Preserve existing sibling fields for compatibility.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
