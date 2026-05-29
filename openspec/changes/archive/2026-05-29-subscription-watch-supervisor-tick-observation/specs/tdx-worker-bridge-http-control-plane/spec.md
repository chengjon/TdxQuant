## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include latest supervisor-tick observation

The worker bridge `watch/status?view=diagnostics` response SHALL include compact latest supervisor-tick observation when present in the detailed status payload.

#### Scenario: Caller requests diagnostics after supervisor tick

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the bridge MUST include `diagnostics.supervisor_tick_observation` when the control payload contains `last_supervisor_tick_observation`
- **AND** the projection MUST include only compact observation fields
- **AND** it MUST NOT expose raw restart backoff, raw start results, raw start requests, logs, file paths, provider credentials, or execute lifecycle control.
