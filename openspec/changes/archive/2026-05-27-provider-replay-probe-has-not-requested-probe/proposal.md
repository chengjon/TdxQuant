# Proposal: Provider Replay Probe Has Not Requested Probe

## Why

`provider-replay status --probe-*` already reports `not_requested`, `not_requested_count`, and `primary_not_requested_probe`.
Callers that only need a compact summary still have to inspect the list or count to know whether configured probes were skipped by the current request.

## What Changes

- Add additive read-only `runtime.probe_summary.has_not_requested_probe`.
- Derive it from existing normalized not-requested probe output.
- Preserve existing probe counts, request coverage status, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
