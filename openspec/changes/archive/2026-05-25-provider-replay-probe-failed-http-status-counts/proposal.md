## Why

Provider replay status now separates requested HTTP status counts from healthy HTTP status counts. The remaining diagnostic gap is the HTTP status distribution for requested probes that are not healthy, such as `503` or `504`, without requiring callers to inspect individual probe payloads.

Adding `failed_http_status_counts` keeps E-06 evidence compact and read-only while making degraded probe composition explicit.

## What Changes

- Add `runtime.probe_summary.failed_http_status_counts` to provider replay status output.
- Count integer `http_status` values only for requested probes whose normalized status is not `healthy`.
- Keep the field empty when no failed probe exposes an integer HTTP status.
- Preserve read-only probe behavior; do not add daemon lifecycle, scheduler, restart, or provider mutation behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused provider replay/API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
