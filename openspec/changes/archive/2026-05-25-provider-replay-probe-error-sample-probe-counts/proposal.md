## Why

`runtime.probe_summary.error_sample_count` and `error_sample_status_counts` show how many probe results qualified for compact error samples and which statuses produced them. Operators still cannot see which probe keys produced those candidates without reading the bounded `error_samples` list, and that list can be truncated.

## What Changes

- Add additive `runtime.probe_summary.error_sample_probe_counts`.
- Derive it from the same candidate set used for `error_samples`, `error_sample_count`, and `error_sample_status_counts`.
- Keep existing `failed_status_counts`, `error_code_counts`, and sample truncation semantics unchanged.

## Impact

- No new HTTP probes, sockets, daemon lifecycle, restart/backoff, scheduler, or provider mutation behavior.
- Summary view keeps mirroring the complete `probe_summary`.
- Existing consumers remain compatible because the field is additive.

