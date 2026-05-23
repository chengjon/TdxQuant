## ADDED Requirements

### Requirement: Worker bridge watch-status SHALL forward reconnect staleness threshold

The worker bridge watch-status HTTP endpoint SHALL accept the optional `reconnect_stale_after_seconds` query parameter and forward it into the read-only subscription watch status summary without changing existing detailed or summary view semantics.

#### Scenario: Caller requests reconnect staleness evaluation

- **WHEN** a caller invokes `GET /bridge/v1/watch/status?reconnect_stale_after_seconds=60`
- **THEN** the bridge MUST pass `reconnect_stale_after_seconds=60.0` to the background watch status controller
- **AND** the response MUST preserve the normal watch-status success envelope

#### Scenario: Caller omits reconnect staleness evaluation

- **WHEN** a caller invokes `GET /bridge/v1/watch/status` without `reconnect_stale_after_seconds`
- **THEN** the bridge MUST preserve existing watch-status behavior
