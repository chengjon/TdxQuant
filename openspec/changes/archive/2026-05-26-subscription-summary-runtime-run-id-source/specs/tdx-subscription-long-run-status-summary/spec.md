## ADDED Requirements

### Requirement: Subscription summary runtime SHALL expose run-id source

Subscription long-run HTTP and CLI summary views SHALL include a read-only `runtime.run_id_source` field derived from the source that supplied `runtime.run_id`, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary view includes runtime run-id source

- **WHEN** a caller requests `watch/status?view=summary` and the underlying status payload supplies `runtime.run_id` from `watch_status.run_id` or `control.run_id`
- **THEN** the HTTP summary result MUST include `runtime.run_id_source` equal to `watch_status` when `watch_status.run_id` is present
- **AND** the HTTP summary result MUST include `runtime.run_id_source` equal to `control` when `watch_status.run_id` is absent and `control.run_id` supplies the value
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged

#### Scenario: CLI summary view includes runtime run-id source

- **WHEN** a caller runs `bridge watch-status --view summary` and the underlying status payload supplies `runtime.run_id` from `watch_status.run_id` or `control.run_id`
- **THEN** the CLI summary result MUST include `runtime.run_id_source` equal to `watch_status` when `watch_status.run_id` is present
- **AND** the CLI summary result MUST include `runtime.run_id_source` equal to `control` when `watch_status.run_id` is absent and `control.run_id` supplies the value
- **AND** reconnect, backoff, restart, lifecycle, SSE, and event-stream behavior MUST remain unchanged
