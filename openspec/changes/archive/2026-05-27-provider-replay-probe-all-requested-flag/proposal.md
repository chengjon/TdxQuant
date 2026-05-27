# Proposal: Provider Replay Probe All Requested Flag

## Why

`runtime.probe_summary.outcome_summary.all_probes_requested` already reports whether the current status request covered every configured probe.
Callers using the top-level `probe_summary` fields still need to inspect `outcome_summary` or compare counts to get the same compact request-coverage signal.

## What Changes

- Add additive read-only top-level `runtime.probe_summary.all_probes_requested`.
- Derive it from the existing request coverage calculation already used by `outcome_summary`.
- Preserve existing request coverage status, counts, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary and provider replay CLI/status tests
