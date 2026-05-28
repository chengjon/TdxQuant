## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose supervision summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.supervision_summary` metadata that describes current supervisor and process tracking state as unavailable.

#### Scenario: Detailed status reports provider replay is not supervised

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.supervision_summary.supervision_status` MUST be `not_supervised`
- **AND** `lifecycle.supervision_summary.supervisor_configured` MUST be `false`
- **AND** `lifecycle.supervision_summary.supervisor_type` MUST be `none`
- **AND** `lifecycle.supervision_summary.managed_process_count` MUST be `0`
- **AND** `lifecycle.supervision_summary.active_process_count` MUST be `0`
- **AND** `lifecycle.supervision_summary.desired_state` MUST be `unmanaged`
- **AND** `lifecycle.supervision_summary.observed_state` MUST be `not_observed`
- **AND** `lifecycle.supervision_summary.process_identity_status` MUST be `not_tracked`
- **AND** `lifecycle.supervision_summary.state_file_status` MUST be `not_configured`
- **AND** `lifecycle.supervision_summary.pid_status` MUST be `not_tracked`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Summary view projects lifecycle supervision without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.supervision_summary` MUST match the detailed lifecycle supervision summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, supervise, write or read state files, track pids, read process tables, infer ownership from ports, run timers, schedule retries, or enable write behavior

#### Scenario: Supervision summary remains a boundary declaration

- **WHEN** lifecycle supervision summary is present
- **THEN** it MUST NOT be treated as process ownership proof, readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future supervisor behavior MUST still require explicit implementation, process ownership proof, lifecycle state storage, and opt-in control semantics
