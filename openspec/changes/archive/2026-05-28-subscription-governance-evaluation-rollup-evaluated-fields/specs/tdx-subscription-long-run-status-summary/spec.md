## ADDED Requirements

### Requirement: Subscription governance evaluation rollup SHALL expose evaluated-component fields

HTTP and CLI watch-status summary views SHALL include additive read-only `governance.evaluation_rollup` evaluated-component fields derived from existing advisory `governance.evaluation_summary` data without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: HTTP summary exposes evaluated-component rollup fields

- **WHEN** a caller requests background watch status with `view=summary`
- **THEN** `governance.evaluation_rollup.primary_evaluated_component` MUST mirror `governance.evaluation_summary.primary_evaluated_component`
- **AND** `governance.evaluation_rollup.has_evaluated_component` MUST indicate whether `governance.evaluation_summary.evaluated_count` is greater than zero
- **AND** the response MUST remain a read-only projection.

#### Scenario: CLI summary exposes evaluated-component rollup fields

- **WHEN** a caller runs `bridge watch-status --view summary`
- **THEN** `governance.evaluation_rollup.primary_evaluated_component` MUST mirror `governance.evaluation_summary.primary_evaluated_component`
- **AND** `governance.evaluation_rollup.has_evaluated_component` MUST indicate whether `governance.evaluation_summary.evaluated_count` is greater than zero
- **AND** the command MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

