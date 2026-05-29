## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include restart backoff guard

The worker bridge HTTP diagnostics projection SHALL include the subscription restart backoff guard summary without changing default detailed status, summary status, restart, restart-preflight, event, stream, start, or stop behavior.

#### Scenario: Caller requests diagnostics with restart backoff guard

- **WHEN** a caller requests worker bridge watch-status with `view=diagnostics`
- **AND** the detailed controller status contains active `control.restart_backoff`
- **THEN** the bridge MUST include `result.diagnostics.restart_backoff.active` as `true`
- **AND** the bridge MUST preserve compact retry metadata emitted by the diagnostics builder
- **AND** the bridge MUST NOT call restart preflight, stop, start, restart, schedule automatic retry, run a supervisor loop, infer ownership from port state, or change SSE/event-stream behavior.
