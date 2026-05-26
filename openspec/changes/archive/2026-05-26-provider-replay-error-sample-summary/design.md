## Design

`runtime.probe_summary.error_sample_summary` is a projection-only metadata rollup emitted with provider replay status probe summaries. It duplicates the existing scalar diagnostics in one object so consumers can inspect compact sample completeness without walking several sibling fields.

Shape:

```json
{
  "count": 4,
  "visible_count": 3,
  "hidden_count": 1,
  "limit": 3,
  "truncated": true,
  "primary_probe": "health",
  "primary_status": "error",
  "primary_error_code": "connection_failed",
  "primary_http_status": 503,
  "primary_reachability": "unreachable"
}
```

Rules:

- Counts are non-negative integers.
- `hidden_count` is derived as `max(count - visible_count, 0)`.
- `truncated` matches the existing `error_sample_truncated` field.
- Primary fields mirror the existing `primary_error_sample_*` sibling fields.
- Existing sibling fields remain available for compatibility.

## Boundaries

This change does not add a provider endpoint, probe target, retry policy, scheduler, socket startup, provider mutation, daemon lifecycle manager, health/readiness guarantee, endpoint coverage proof, or service ownership proof. It is an additive read-only status projection.
