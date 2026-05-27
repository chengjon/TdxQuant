# Proposal: Provider Replay Probe Has Requested Probe

## Why

`provider-replay status --probe-*` already reports `requested`, `requested_count`, and `primary_requested_probe`.
Callers that only need a compact status envelope still have to inspect the list or count to know whether the current request asked for any configured probe.

## What Changes

- Add additive read-only top-level `runtime.probe_summary.has_requested_probe`.
- Derive it from existing normalized requested probe output.
- Preserve existing request coverage status, counts, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
