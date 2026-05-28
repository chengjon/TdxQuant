## ADDED Requirements

### Requirement: Provider replay lifecycle status SHALL expose backoff summary

Provider replay lifecycle status SHALL include additive read-only `lifecycle.backoff_summary` metadata that describes current supervised backoff state as unavailable.

#### Scenario: Detailed status reports backoff is not configured

- **WHEN** provider replay status is built with the current non-lifecycle-managing implementation
- **THEN** `lifecycle.backoff_summary.backoff_status` MUST be `not_configured`
- **AND** `lifecycle.backoff_summary.enabled` MUST be `false`
- **AND** `lifecycle.backoff_summary.policy` MUST be `not_managed`
- **AND** `lifecycle.backoff_summary.retry_count` MUST be `0`
- **AND** `lifecycle.backoff_summary.next_retry_status` MUST be `not_scheduled`
- **AND** `lifecycle.backoff_summary.next_retry_pending` MUST be `false`
- **AND** the summary MUST identify lifecycle control as not implemented

#### Scenario: Summary view projects lifecycle backoff without adding control

- **WHEN** a caller requests `provider-replay status --view summary`
- **THEN** `summary_view.lifecycle.backoff_summary` MUST match the detailed lifecycle backoff summary
- **AND** the existing detailed `status` payload MUST remain available
- **AND** the command MUST NOT start, stop, restart, daemonize, schedule, supervise, write state files, read process tables, infer ownership from ports, run timers, or enable write behavior

#### Scenario: Backoff summary remains a boundary declaration

- **WHEN** lifecycle backoff summary is present
- **THEN** it MUST NOT be treated as readiness, broker availability, endpoint coverage, workflow readiness, write-capability proof, automatic recovery, or a scheduled retry
- **AND** future supervised backoff MUST still require explicit implementation, opt-in policy, bounded retry rules, and ownership proof where required

