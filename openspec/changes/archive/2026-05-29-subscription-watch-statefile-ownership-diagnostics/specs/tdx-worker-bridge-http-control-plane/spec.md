## ADDED Requirements

### Requirement: Worker bridge diagnostics SHALL include statefile ownership diagnostics

The worker bridge `watch/status?view=diagnostics` response SHALL include the compact subscription-watch `statefile_ownership` diagnostic.

#### Scenario: Caller requests diagnostics with statefile ownership

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the bridge MUST include `diagnostics.statefile_ownership`
- **AND** the projected diagnostic MUST include schema version, status, reason codes, PID match/liveness booleans, and boundary
- **AND** the diagnostics response MUST NOT expose raw control payload, raw watch-status payload, raw file paths, or execute lifecycle control.

