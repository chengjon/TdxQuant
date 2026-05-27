# Proposal: Provider Replay Probe Has Error Sample

## Why

`provider-replay status --probe-*` exposes error sample counts and bounded sample details, but compact consumers must compare `error_sample_count` to determine whether any probe error sample exists. E-06 remains partial, so this should be a read-only diagnostic hint rather than daemon management or probe execution behavior.

## What Changes

- Add additive read-only `runtime.probe_summary.has_error_sample`.
- Derive it from existing normalized `error_sample_count`.
- Preserve existing bounded `error_samples`, primary error-sample fields, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary builder, focused provider replay/CLI tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
