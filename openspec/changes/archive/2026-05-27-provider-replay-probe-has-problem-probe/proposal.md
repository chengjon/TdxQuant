# Proposal: Provider Replay Probe Has Problem Probe

## Why

`runtime.probe_summary.primary_problem_probe` already identifies the first failed, unhealthy, or error-sample probe candidate.
Compact consumers still need to test that field for null to know whether the status payload has any problem probe candidate.

## What Changes

- Add additive read-only top-level `runtime.probe_summary.has_problem_probe`.
- Derive it from existing normalized problem probe selection.
- Preserve existing primary probe hints, counts, error-sample metadata, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
