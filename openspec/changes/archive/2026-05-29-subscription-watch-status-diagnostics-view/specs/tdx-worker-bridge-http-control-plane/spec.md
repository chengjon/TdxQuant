## ADDED Requirements

### Requirement: Worker bridge watch-status SHALL expose diagnostics view

The worker bridge HTTP control plane SHALL allow callers to request a compact read-only diagnostics projection from `GET /bridge/v1/watch/status?view=diagnostics` without changing the default detailed response, existing summary view, or lifecycle behavior.

#### Scenario: Caller requests watch-status diagnostics view

- **WHEN** a caller requests `GET /bridge/v1/watch/status?view=diagnostics`
- **THEN** the bridge MUST return a compact payload with `mode` equal to `diagnostics`
- **AND** the payload MUST include a top-level `diagnostics` object derived from existing summary rollups
- **AND** the payload MUST NOT include raw `control`, raw `watch_status`, full governance `reasons`, or full governance `actions`
- **AND** the bridge MUST NOT acquire locks, read PID files, signal processes, prove ownership, prove readiness, or trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Unsupported view message includes diagnostics

- **WHEN** a caller requests `GET /bridge/v1/watch/status` with an unsupported `view` value
- **THEN** the validation error MUST list `detailed`, `summary`, and `diagnostics` as supported values.
