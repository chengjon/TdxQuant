## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include restartability summary

The worker bridge HTTP diagnostics projection SHALL include the subscription restartability summary without changing default detailed status, summary status, restart, restart-preflight, event, stream, start, or stop behavior.

#### Scenario: Caller requests diagnostics with restartability summary

- **WHEN** a caller invokes `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the bridge MUST include `result.diagnostics.restartability`
- **AND** the projection MUST be derived from the existing watch-status result
- **AND** the bridge MUST NOT call restart preflight, stop, start, restart, schedule automatic backoff, run a supervisor loop, infer ownership from port state, or change SSE/event-stream behavior.
