# Proposal: Provider Replay Probe Top-Level Has Failed Probe

## Why

`runtime.probe_summary.failed_count`, `failed`, and `primary_failed_probe` already expose failed probe details.
`outcome_summary.has_failed_probe` also exists, but top-level compact consumers still have to inspect the nested outcome summary or compare counts to know whether any requested probe failed.

## What Changes

- Add additive read-only top-level `runtime.probe_summary.has_failed_probe`.
- Derive it from the existing failed probe count/list.
- Preserve existing outcome summary, counts, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
