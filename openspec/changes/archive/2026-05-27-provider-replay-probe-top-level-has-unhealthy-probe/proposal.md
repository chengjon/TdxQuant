# Proposal: Provider Replay Probe Top-Level Has Unhealthy Probe

## Why

`runtime.probe_summary.unhealthy_count`, `unhealthy`, and `primary_unhealthy_probe` already expose unhealthy probe details.
`outcome_summary.has_unhealthy_probe` also exists, but top-level compact consumers still have to inspect the nested outcome summary or compare counts to know whether any probe normalized to an unhealthy state.

## What Changes

- Add additive read-only top-level `runtime.probe_summary.has_unhealthy_probe`.
- Derive it from the existing normalized unhealthy probe list.
- Preserve existing outcome summary, counts, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
