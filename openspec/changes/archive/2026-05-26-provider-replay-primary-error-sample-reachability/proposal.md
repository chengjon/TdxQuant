# Add provider replay primary error sample reachability

## Why

Provider replay probe summaries now expose error sample reachability counts. Operators can see the distribution, but the compact primary error sample diagnostics still identify only the first sample's probe, status, error code, and HTTP status.

E-06 remains partial in `FUNCTION_TREE.md` because this surface is replay-only and read-only. Adding the first error sample's reachability bucket improves compact diagnostics without changing probe execution or daemon lifecycle behavior.

## What Changes

- Add read-only `runtime.probe_summary.primary_error_sample_reachability`.
- Derive it from the first existing error sample candidate using the same `reachable` / `unreachable` / `unknown` bucket semantics.
- Return `null` when there is no error sample candidate.
- Do not change `error_samples` payload shape, probe execution, configured endpoints, socket startup, replay lifecycle, restart/backoff, daemon management, or provider mutation behavior.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Touches provider replay probe summary rollup code only.
- Adds focused provider replay detailed and CLI summary assertions.
- Updates `FUNCTION_TREE.md` as the single registry with explicit E-06 status, evidence, and boundary.
