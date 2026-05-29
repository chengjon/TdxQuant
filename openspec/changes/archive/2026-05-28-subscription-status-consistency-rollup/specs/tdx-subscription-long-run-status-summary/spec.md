## ADDED Requirements

### Requirement: Subscription status summary SHALL expose consistency rollup

Subscription long-run status summaries SHALL include additive read-only `status_summary.consistency_rollup` metadata derived from existing `control` and `watch_status` payloads without changing lock handling, PID-file reads, PID liveness checks, process ownership, restart, backoff, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes consistency rollup

- **WHEN** `build_subscription_watch_status_summary()` receives `control` and `watch_status` payloads
- **THEN** `status_summary.consistency_rollup.control_state` MUST mirror `control.state` or be `unknown` when absent
- **AND** `status_summary.consistency_rollup.watch_state` MUST mirror `watch_status.state` or be `null` when absent
- **AND** `status_summary.consistency_rollup.has_watch_status` MUST be true only when `watch_status` is a non-empty object
- **AND** `status_summary.consistency_rollup.has_control_run_id` MUST be true only when `control.run_id` is a non-empty string
- **AND** `status_summary.consistency_rollup.has_watch_run_id` MUST be true only when `watch_status.run_id` is a non-empty string
- **AND** `status_summary.consistency_rollup.run_id_match` MUST compare run IDs only when both run IDs are present, otherwise be `null`
- **AND** `status_summary.consistency_rollup.state_match` MUST compare states only when both states are present, otherwise be `null`
- **AND** `status_summary.consistency_rollup.has_mismatch` MUST be true only when a comparable state or run ID is explicitly mismatched
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects consistency rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `status_summary.consistency_rollup` when the detailed status summary provides it
- **AND** the response MUST NOT acquire locks, read PID files, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects consistency rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `status_summary.consistency_rollup` when the detailed status summary provides it
- **AND** the command MUST NOT acquire locks, read PID files, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
