## ADDED Requirements

### Requirement: Subscription summary runtime SHALL expose run-id match

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.run_id_match` field derived from `control.run_id` and `watch_status.run_id` when both raw run ids are present, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime run-id match

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload includes both `control.run_id` and `watch_status.run_id`
- **THEN** the HTTP summary result MUST include `runtime.run_id_match` equal to whether those two raw run ids are equal
- **AND** the HTTP summary result MUST continue to expose `runtime.run_id` and `runtime.run_id_source`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime run-id match

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload includes both `control.run_id` and `watch_status.run_id`
- **THEN** the CLI summary result MUST include `runtime.run_id_match` equal to whether those two raw run ids are equal
- **AND** the CLI summary result MUST continue to expose `runtime.run_id` and `runtime.run_id_source`
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged
