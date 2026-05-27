# provider replay probe advisory summary

## Why

Provider replay probe status now exposes several focused rollups: request coverage, health posture, outcome posture, count maps, target lists, and primary probe hints. That is useful for detailed inspection, but consumers that only need a compact "what should I look at first" view still have to coordinate multiple sibling fields.

Adding `runtime.probe_summary.advisory_summary` gives E-06 a stable read-only entry point for dashboards and CLI summary consumers while preserving the fake-provider boundary. It aggregates existing normalized rollup metadata only; it does not execute probes, start sockets, manage daemon lifecycle, or enable writes.

## What Changes

- Add read-only `runtime.probe_summary.advisory_summary`.
- Populate it from existing probe summary metadata:
  - overall status and request coverage status
  - total/requested/healthy/failed/unhealthy counts
  - requested/healthy/failed/unhealthy/problem presence flags
  - primary problem probe and primary error-sample probe hints
  - an explicit read-only boundary marker
- Keep detailed sibling fields and nested summaries unchanged for compatibility.
- Ensure CLI summary view exposes the object through the existing copied `probe_summary`.
- Update focused tests, OpenSpec, and `FUNCTION_TREE.md` E-06 evidence/boundary notes.

## Impact

- Affected code: `tdxquant/provider_transport_replay.py`
- Affected tests: `tests/test_provider_transport_replay.py`, `tests/test_api_cli.py`
- Affected specs: `tdx-provider-transport-replay-service`
- Verification: focused pytest for provider replay/API CLI, OpenSpec strict validation, diff whitespace check, FUNCTION_TREE registry validation

