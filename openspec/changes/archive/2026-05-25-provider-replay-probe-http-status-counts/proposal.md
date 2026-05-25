## Why

Provider replay probe summaries expose status and reachability rollups, but they do not summarize HTTP status codes from requested probes. A compact HTTP-status map helps distinguish successful HTTP responses from transport or HTTP failures without expanding raw probe payloads.

## What Changes

- Add additive `runtime.probe_summary.requested_http_status_counts`.
- Count only requested fixed probe targets with integer `http_status` values.
- Use stringified HTTP status codes as JSON object keys.
- Mirror the field through `provider-replay status --view summary` because summary view carries the existing `probe_summary`.
- Keep behavior read-only; do not add probes, start sockets, manage daemon lifecycle, or change replay transport behavior.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected registry: `FUNCTION_TREE.md` E-06 evidence and boundary
