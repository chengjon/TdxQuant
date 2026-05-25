## Why

`provider-replay status --probe-* --view summary` already exposes compact probe error samples plus `error_sample_limit` and `error_sample_truncated`, but it does not expose the total number of probe results that qualified for the sample set. Operators can see that the list was truncated, yet cannot distinguish "exactly the listed samples" from "more errors existed" without reading the detailed payload.

## What Changes

- Add additive `runtime.probe_summary.error_sample_count`.
- Derive the count from the same read-only probe objects already used for `error_samples` and `error_sample_truncated`.
- Preserve summary view behavior by projecting the complete `probe_summary`, including the new count.

## Impact

- No new probe endpoints, socket startup, daemon lifecycle, restart/backoff, provider mutation, or scheduler behavior.
- Existing payloads remain backward compatible; the new field is additive.
- Tests will cover both detailed status and summary view projection.
