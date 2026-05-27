# provider replay probe health summary

## Why

Provider replay status already exposes probe health posture through sibling fields such as `status`, healthy/failed/unhealthy counts, status-count maps, and primary healthy/failed/unhealthy probes. Consumers that only need compact health posture currently have to reconstruct it from several fields.

Adding `runtime.probe_summary.health_summary` keeps E-06 evidence compact while preserving the fake-provider boundary: it summarizes existing probe metadata only and does not start sockets, manage daemon lifecycle, execute unrequested probes, or enable writes.

## What Changes

- Add read-only `runtime.probe_summary.health_summary` to provider replay status.
- Derive the object from existing probe summary fields:
  - overall status
  - healthy/failed/unhealthy counts
  - status key count
  - primary healthy, failed, and unhealthy probes
- Keep existing sibling fields for compatibility.
- Ensure CLI summary view continues to expose the object through the copied `probe_summary`.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence and boundary text.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation
