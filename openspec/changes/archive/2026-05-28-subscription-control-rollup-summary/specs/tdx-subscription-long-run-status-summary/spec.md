## ADDED Requirements

### Requirement: Subscription status summary SHALL expose control rollup

Subscription long-run status summaries SHALL include additive read-only `status_summary.control_rollup` metadata derived from the existing reconciled `control` payload without changing lock handling, PID liveness checks, process ownership, restart, backoff, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes control rollup

- **WHEN** `build_subscription_watch_status_summary()` receives a reconciled `control` payload
- **THEN** `status_summary.control_rollup.control_state` MUST mirror `control.state` or be `unknown` when absent
- **AND** `status_summary.control_rollup.control_active` MUST mirror boolean `control.active`
- **AND** `status_summary.control_rollup.has_control_run_id` MUST be true only when `control.run_id` is a non-empty string
- **AND** `status_summary.control_rollup.has_control_pid` MUST be true only when `control.pid` is a positive non-boolean integer
- **AND** `status_summary.control_rollup.control_reason` MUST mirror `control.reason` or be `null` when absent
- **AND** `status_summary.control_rollup.stale_process_state` MUST be true only when `control.reason` equals `stale_process_state`
- **AND** `status_summary.control_rollup.startup_persistence_failed` MUST be true only when `control.reason` equals `startup_persistence_failed`
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects control rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `status_summary.control_rollup` when the detailed status summary provides it
- **AND** the response MUST NOT acquire locks, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects control rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `status_summary.control_rollup` when the detailed status summary provides it
- **AND** the command MUST NOT acquire locks, signal processes, prove ownership, or trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
