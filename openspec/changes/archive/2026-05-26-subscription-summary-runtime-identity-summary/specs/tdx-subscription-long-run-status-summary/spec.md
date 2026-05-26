## ADDED Requirements

### Requirement: Watch-status summary SHALL expose runtime identity summary

HTTP and CLI watch-status summary views SHALL include additive read-only `runtime.identity_summary` metadata derived from existing runtime identity fields without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary includes runtime identity summary

- **WHEN** a caller requests bridge HTTP `watch/status?view=summary`
- **THEN** the response MUST include `runtime.identity_summary`
- **AND** it MUST derive control/watch state, state match, run ID presence/source/match, and PID presence/source from existing runtime summary sibling fields
- **AND** existing runtime sibling fields MUST remain available
- **AND** the summary MUST NOT expose raw control payloads, raw watch-status payloads, event-stream data, lifecycle controls, or executable instructions

#### Scenario: CLI summary includes runtime identity summary

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `runtime.identity_summary`
- **AND** `has_run_id`, `run_id_source`, `run_id_match`, `has_pid`, and `pid_source` MUST match the existing compact runtime sibling fields
- **AND** the summary MUST NOT prove PID liveness, run ownership, run freshness, health/readiness, or process ownership
- **AND** the summary MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
