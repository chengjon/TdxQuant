# Add provider replay error sample reachability counts

## Why

Provider replay probe summaries already expose requested, healthy-only, and failed-only reachability count maps. They also expose compact error sample candidates plus HTTP status distribution for that candidate set, but not the reachability distribution for the same error sample candidate set.

E-06 remains partial in `FUNCTION_TREE.md` because the fake provider is still a replay-only, foreground, read-only diagnostic surface without daemon lifecycle control. Adding error-sample reachability counts improves diagnostics while staying inside that boundary.

## What Changes

- Add read-only `runtime.probe_summary.error_sample_reachability_counts`.
- Add read-only `runtime.probe_summary.error_sample_reachability_key_count`.
- Mirror the fields through `provider-replay status --view summary` because the summary view projects the same `probe_summary`.
- Do not change probe execution, configured endpoints, socket startup, replay lifecycle, restart/backoff, daemon management, or provider mutation behavior.

## Capabilities

### Modified Capabilities

- `tdx-provider-transport-replay-service`

## Impact

- Touches provider replay probe summary rollup code only.
- Adds focused provider replay detailed and CLI summary assertions.
- Updates `FUNCTION_TREE.md` as the single registry with explicit E-06 status, evidence, and boundary.
