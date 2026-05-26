# subscription summary runtime identity summary design

## Design

`runtime.identity_summary` is emitted only by HTTP and CLI watch-status summary views. It is a compact rollup of existing runtime identity sibling fields and contains no raw control payload, raw watch-status payload, event-stream data, lifecycle controls, or executable instructions.

Shape:

```json
{
  "control_state": "running",
  "watch_state": "running",
  "state_match": true,
  "has_run_id": true,
  "run_id_source": "watch_status",
  "run_id_match": true,
  "has_pid": true,
  "pid_source": "control"
}
```

Rules:

- The object is derived only from fields already projected in `runtime`.
- Existing sibling fields remain available for compatibility.
- `has_run_id` and `has_pid` describe presence in the compact runtime view; they do not prove freshness, ownership, or liveness.
- The object does not trigger reconnect, backoff, restart, lifecycle changes, HTTP control actions, SSE behavior, or event-stream behavior.

## Boundaries

This change does not add PID liveness checks, process ownership proof, run freshness proof, restart/backoff policy, production process management, raw payload disclosure, or event-stream behavior. It is an additive non-executing summary projection.
