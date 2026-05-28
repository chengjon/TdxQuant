## ADDED Requirements

### Requirement: Subscription governance summary SHALL expose reconnect rollup

Subscription long-run status summaries SHALL include additive read-only `governance.reconnect_rollup` metadata derived from existing reconnect diagnostics without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Core status summary exposes reconnect rollup

- **WHEN** `build_subscription_watch_status_summary()` builds reconnect diagnostics
- **THEN** `governance.reconnect_rollup.staleness` MUST mirror `reconnect.staleness`
- **AND** `governance.reconnect_rollup.reconnect_count` MUST mirror `reconnect.reconnect_count`
- **AND** `governance.reconnect_rollup.consecutive_reconnect_failures` MUST mirror `reconnect.consecutive_reconnect_failures`
- **AND** `governance.reconnect_rollup.has_reconnects` MUST be true only when `reconnect_count` is a positive non-boolean integer
- **AND** `governance.reconnect_rollup.has_reconnect_failures` MUST be true only when `consecutive_reconnect_failures` is a positive non-boolean integer
- **AND** `governance.reconnect_rollup.has_last_error` MUST be true only when `reconnect.last_error` is a non-empty object
- **AND** `governance.reconnect_rollup.has_next_reconnect_at` MUST be true only when `reconnect.next_reconnect_at` is a non-empty string
- **AND** the rollup MUST remain a read-only projection.

#### Scenario: HTTP summary view projects reconnect rollup

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** the response MUST include `governance.reconnect_rollup` when the detailed governance payload provides it
- **AND** the response MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: CLI summary view projects reconnect rollup

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** the printed summary payload MUST include `governance.reconnect_rollup` when the detailed governance payload provides it
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
