# provider replay probe request summary

## Why

Provider replay status already exposes probe request coverage as sibling fields: `request_coverage_status`, total/requested/not-requested counts, health/failure counts, and primary probe pointers. Consumers that only need a compact read-only request coverage rollup currently have to reconstruct it from many siblings.

Adding `runtime.probe_summary.request_summary` keeps E-06 evidence compact while preserving the fake-provider boundary: it summarizes existing probe metadata only and does not start sockets, manage daemon lifecycle, execute unrequested probes, or enable writes.

## What Changes

- Add read-only `runtime.probe_summary.request_summary` to provider replay status.
- Derive the object from existing probe summary fields:
  - request coverage status
  - total/requested/not-requested counts
  - healthy/failed/unhealthy counts
  - primary requested and not-requested probes
- Keep existing sibling fields for compatibility.
- Ensure CLI summary view continues to expose the object through the copied `probe_summary`.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
