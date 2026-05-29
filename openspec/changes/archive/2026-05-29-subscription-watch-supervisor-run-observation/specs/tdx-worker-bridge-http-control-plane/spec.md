## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include latest supervisor-run observation

The worker bridge `watch/status?view=diagnostics` response SHALL include compact latest supervisor-run observation when present in the detailed status payload.

#### Scenario: Caller requests diagnostics after supervisor run

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the bridge MUST include `diagnostics.supervisor_run_observation` when the control payload contains `last_supervisor_run_observation`
- **AND** the projection MUST include only compact observation fields
- **AND** it MUST NOT expose raw tick summaries, raw start results, raw start requests, logs, file paths, or execute lifecycle control.

