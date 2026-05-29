## ADDED Requirements

### Requirement: Subscription watch-status SHALL expose read-only diagnostics view

HTTP and CLI watch-status commands SHALL expose an opt-in diagnostics view derived from existing summary rollups without changing reconnect, backoff, restart, lifecycle, HTTP route defaults, SSE, or event-stream behavior.

#### Scenario: CLI diagnostics view projects combined diagnostics

- **WHEN** a caller runs `bridge watch-status --view diagnostics`
- **THEN** the command MUST emit a compact payload with `result.mode` equal to `diagnostics`
- **AND** the payload MUST include a top-level `result.diagnostics` object
- **AND** diagnostics fields MUST be derived from existing summary rollups
- **AND** the command MUST NOT acquire locks, read PID files, signal processes, prove ownership, prove readiness, or trigger reconnect, backoff, restart, lifecycle, SSE, or event-stream behavior.

#### Scenario: Diagnostics view does not expose raw payloads

- **WHEN** diagnostics view is requested
- **THEN** the result MUST NOT expose raw `control` or raw `watch_status`
- **AND** the result MUST NOT expose full governance `reasons` or full governance `actions`.
