# Proposal: Provider Replay Probe Has Healthy Probe

## Why

`provider-replay status --probe-*` exposes `healthy_count`, `healthy`, and `primary_healthy_probe`, while also exposing boolean hints for failed and unhealthy probes. Compact consumers still need to compare counts or inspect arrays to know whether any requested probe was healthy. E-06 remains partial, so this should be a read-only diagnostic hint rather than daemon management or readiness behavior.

## What Changes

- Add additive read-only `runtime.probe_summary.has_healthy_probe`.
- Derive it from existing normalized healthy probe output.
- Preserve existing probe counts, primary probe hints, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary builder, focused provider replay/CLI tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
