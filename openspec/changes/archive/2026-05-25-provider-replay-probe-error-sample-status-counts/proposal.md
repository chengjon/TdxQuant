## Why

`runtime.probe_summary.error_sample_count` exposes how many probe results qualified for compact error samples, but operators still cannot see the status distribution of that same candidate set without reading individual samples. The existing `failed_status_counts` intentionally excludes healthy probes and is tied to failed classification, so it is not the same question as "what statuses produced error sample candidates?"

## What Changes

- Add additive `runtime.probe_summary.error_sample_status_counts`.
- Derive it from the same candidate set used for `error_samples` and `error_sample_count`.
- Preserve `failed_status_counts` as the non-healthy requested probe distribution.

## Impact

- No new HTTP probes, sockets, daemon lifecycle, restart/backoff, scheduler, or provider mutation behavior.
- Summary view keeps mirroring the complete `probe_summary`.
- Existing consumers remain compatible because the field is additive.
