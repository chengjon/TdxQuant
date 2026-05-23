## MODIFIED Requirements

### Requirement: Worker bridge watch-status SHALL expose an opt-in HTTP summary view

The worker bridge HTTP control plane SHALL allow callers to request a compact read-only summary projection from `GET /bridge/v1/watch/status` without changing the default detailed response or lifecycle behavior.

#### Scenario: Caller omits watch-status view

- **WHEN** a caller requests `GET /bridge/v1/watch/status` without a `view` query parameter
- **THEN** the bridge MUST return the existing detailed controller status payload
- **AND** the bridge MUST continue forwarding explicit heartbeat and watermark stale thresholds

#### Scenario: Caller requests watch-status summary view

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=summary`
- **THEN** the bridge MUST call the existing controller status path once
- **AND** the bridge MUST return a compact success envelope with `result.mode=summary`
- **AND** the result MUST include the worker id, status, selected `status_summary` fields, selected runtime identity fields, and advisory `governance.action_summary` when present
- **AND** the result MUST NOT include raw `control` or `watch_status` payloads

#### Scenario: Caller requests unsupported watch-status view

- **WHEN** a caller requests `GET /bridge/v1/watch/status` with an unsupported `view` value
- **THEN** the bridge MUST reject the request as invalid before writing a success response
- **AND** the bridge MUST NOT start, stop, restart, reconnect, back off, or change event-stream behavior
