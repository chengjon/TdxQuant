## Design

`governance.sample_summary` is a read-only metadata rollup for compact summary views. The field is emitted only by summary projections and only when the corresponding underlying `governance.reasons` and/or `governance.actions` lists are present.

Shape:

```json
{
  "reason_count": 4,
  "reason_sample_count": 3,
  "reason_sample_hidden_count": 1,
  "reason_sample_limit": 3,
  "reason_sample_truncated": true,
  "action_count": 4,
  "action_sample_count": 3,
  "action_sample_hidden_count": 1,
  "action_sample_limit": 3,
  "action_sample_truncated": true
}
```

Rules:

- Counts are non-negative integers.
- Hidden counts are derived as `max(total_count - sample_count, 0)`.
- Truncated flags match the existing sibling `*_sample_truncated` fields.
- Existing sibling fields remain available for compatibility.
- Full `governance.reasons` and `governance.actions` remain omitted from summary views.

## Boundaries

This change does not introduce a governance policy engine, execution queue, escalation workflow, reconnect/backoff strategy, restart behavior, PID liveness proof, health/readiness guarantee, HTTP polling change, SSE change, or event-stream behavior. It is an additive projection-only metadata object.
