# subscription governance decision summary design

## Design

`governance.decision_summary` is emitted only by HTTP and CLI watch-status summary views. It is a compact rollup of existing advisory governance sibling fields and contains no raw control payload, raw watch-status payload, full reasons/actions, event-stream data, lifecycle controls, or executable instructions.

Shape:

```json
{
  "decision": "manual_review",
  "requires_manual_review": true,
  "staleness_evaluated": true,
  "reason_count": 4,
  "action_count": 4,
  "primary_reason_source": "heartbeat",
  "primary_severity": "review"
}
```

Rules:

- The object is derived only from fields already projected in `governance`.
- Existing sibling fields remain available for compatibility.
- Missing optional fields are represented as `null` rather than causing extra evaluation.
- The object does not trigger reconnect, backoff, restart, lifecycle changes, HTTP control actions, SSE behavior, or event-stream behavior.

## Boundaries

This change does not add governance strategy, automatic remediation, reconnect/backoff policy, production process management, raw payload disclosure, full reason/action disclosure, or event-stream behavior. It is an additive non-executing summary projection.
