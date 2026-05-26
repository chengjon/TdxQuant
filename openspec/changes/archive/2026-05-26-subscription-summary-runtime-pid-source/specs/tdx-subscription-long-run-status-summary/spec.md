## ADDED Requirements

### Requirement: Subscription Summary Runtime PID Source

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.pid_source` field derived from the source that supplied `runtime.pid`, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes runtime PID source

- **GIVEN** a subscription watch status payload with `control.pid`
- **WHEN** a caller requests `watch/status?view=summary`
- **THEN** the HTTP summary result MUST include `runtime.pid` from `control.pid`
- **AND** the HTTP summary result MUST include `runtime.pid_source` equal to `control`
- **AND** this field MUST NOT imply PID liveness, process ownership, readiness, or lifecycle control.

#### Scenario: CLI summary includes runtime PID source

- **GIVEN** a subscription watch status payload with `control.pid`
- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the CLI summary result MUST include `runtime.pid` from `control.pid`
- **AND** the CLI summary result MUST include `runtime.pid_source` equal to `control`
- **AND** this field MUST NOT imply PID liveness, process ownership, readiness, or lifecycle control.
