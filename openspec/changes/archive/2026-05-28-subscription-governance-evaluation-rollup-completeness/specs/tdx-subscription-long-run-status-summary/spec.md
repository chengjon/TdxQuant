## ADDED Requirements

### Requirement: Subscription governance evaluation rollup SHALL expose compact completeness fields

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.evaluation_rollup` completeness fields derived from existing advisory `governance.evaluation_summary` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes evaluation rollup completeness

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.evaluation_rollup.has_not_evaluated_component` MUST indicate whether any component was not evaluated
- **AND** `governance.evaluation_rollup.component_status_key_count` MUST mirror `governance.evaluation_summary.component_status_key_count`
- **AND** `governance.evaluation_rollup.evaluated_status_key_count` MUST mirror `governance.evaluation_summary.evaluated_status_key_count`
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes evaluation rollup completeness

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.evaluation_rollup.has_not_evaluated_component` MUST indicate whether any component was not evaluated
- **AND** `governance.evaluation_rollup.component_status_key_count` MUST mirror `governance.evaluation_summary.component_status_key_count`
- **AND** `governance.evaluation_rollup.evaluated_status_key_count` MUST mirror `governance.evaluation_summary.evaluated_status_key_count`
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.
