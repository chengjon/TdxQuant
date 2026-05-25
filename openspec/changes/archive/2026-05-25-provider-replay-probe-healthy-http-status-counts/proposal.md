## Why

Provider replay status already reports requested HTTP status counts and failed error-code counts. Operators can see all requested HTTP statuses, but not the HTTP status distribution of probes that were actually healthy without inspecting individual probe payloads.

Adding `healthy_http_status_counts` keeps the E-06 daemon fake provider registry evidence compact and read-only while making successful probe composition explicit.

## What Changes

- Add `runtime.probe_summary.healthy_http_status_counts` to provider replay status output.
- Count integer `http_status` values only for requested probes whose normalized status is `healthy`.
- Keep the field empty when no healthy probe exposes an integer HTTP status.
- Preserve read-only probe behavior; do not add daemon lifecycle, scheduler, restart, or provider mutation behavior.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused provider replay/API CLI tests plus OpenSpec, diff whitespace, and FUNCTION_TREE registry validation
