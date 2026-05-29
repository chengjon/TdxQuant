## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include latest restart observation

The worker bridge HTTP diagnostics projection SHALL include the subscription latest restart observation summary without changing default detailed status, summary status, restart, restart-preflight, event, stream, start, or stop behavior.

#### Scenario: Caller requests diagnostics with restart observation

- **WHEN** a caller requests worker bridge watch-status with `view=diagnostics`
- **AND** the detailed controller status contains `control.last_restart_observation`
- **THEN** the bridge MUST include `result.diagnostics.restart_observation.has_observation` as `true`
- **AND** the bridge MUST preserve the compact observation fields emitted by the diagnostics builder
- **AND** the bridge MUST NOT call restart preflight, stop, start, restart, schedule automatic backoff, run a supervisor loop, infer ownership from port state, or change SSE/event-stream behavior.
