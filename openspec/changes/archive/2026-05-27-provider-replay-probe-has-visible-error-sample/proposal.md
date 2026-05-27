# Proposal: Provider Replay Probe Has Visible Error Sample

## Why

`provider-replay status --probe-*` exposes `error_sample_visible_count`, but compact consumers must compare that count to determine whether the response currently contains any visible bounded error samples. E-06 remains partial, so this should be a read-only diagnostic hint rather than daemon management or probe execution behavior.

## What Changes

- Add additive read-only `runtime.probe_summary.has_visible_error_sample`.
- Derive it from existing normalized `error_sample_visible_count`.
- Preserve existing bounded `error_samples`, truncation metadata, and non-executing provider replay boundaries.

## Impact

- Affected spec: `tdx-provider-transport-replay-service`
- Affected code: provider replay status summary builder, focused provider replay/CLI tests, and `FUNCTION_TREE.md` E-06 registry evidence/boundary.
