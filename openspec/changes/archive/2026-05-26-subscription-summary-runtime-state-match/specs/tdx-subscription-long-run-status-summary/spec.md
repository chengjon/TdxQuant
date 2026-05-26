## ADDED Requirements

### Requirement: Subscription summary runtime SHALL expose state match

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.state_match` field derived from `control.state` and `watch_status.state` when both source states are present, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime state match

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload includes both `control.state` and `watch_status.state`
- **THEN** the HTTP summary result MUST include `runtime.state_match` equal to whether those two state strings are equal
- **AND** the HTTP summary result MUST continue to expose `runtime.control_state` and `runtime.watch_state`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime state match

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload includes both `control.state` and `watch_status.state`
- **THEN** the CLI summary result MUST include `runtime.state_match` equal to whether those two state strings are equal
- **AND** the CLI summary result MUST continue to expose `runtime.control_state` and `runtime.watch_state`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged
