# subscription decision presence flags design

## Design

The existing `governance.decision_summary` object is a compact read-only rollup emitted by the HTTP and CLI watch-status summary projections. This change extends that object with two additive booleans:

```json
{
  "decision": "manual_review",
  "requires_manual_review": true,
  "staleness_evaluated": true,
  "reason_count": 4,
  "action_count": 4,
  "primary_reason_source": "heartbeat",
  "primary_severity": "review",
  "has_reasons": true,
  "has_actions": true
}
```

Rules:

- `has_reasons` is `true` only when the already-projected `reason_count` is an integer greater than zero.
- `has_actions` is `true` only when the already-projected `action_count` is an integer greater than zero.
- Missing or non-integer count values are treated conservatively as `false`.
- The fields are derived inside the projection layer and do not trigger additional subscription status evaluation.
- Existing decision summary fields and sibling governance fields remain available for compatibility.

## Boundaries

This change is a read-only status projection. It does not add reconnect/backoff policy, restart/lifecycle control, production process management, HTTP control actions, SSE/event-stream behavior, full reason/action disclosure, task/report/trade execution, workflow execution, or readiness/health proof.

