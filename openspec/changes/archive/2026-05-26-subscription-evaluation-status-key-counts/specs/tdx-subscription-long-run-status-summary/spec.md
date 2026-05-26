## ADDED Requirements

### Requirement: Subscription governance evaluation summary SHALL expose status key counts

Subscription long-run status summaries SHALL include additive `status_summary.governance.evaluation_summary.component_status_key_count` and `status_summary.governance.evaluation_summary.evaluated_status_key_count` fields derived from existing evaluation status-count maps without changing staleness evaluation, reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Evaluation summary reports all component status key count

- **WHEN** `governance.evaluation_summary.component_status_counts` contains one or more status keys
- **THEN** `governance.evaluation_summary.component_status_key_count` MUST equal the number of keys in `component_status_counts`
- **AND** existing component lists, scalar counts, and status-count maps MUST remain available

#### Scenario: Evaluation summary reports evaluated status key count

- **WHEN** `governance.evaluation_summary.evaluated_status_counts` contains zero or more status keys
- **THEN** `governance.evaluation_summary.evaluated_status_key_count` MUST equal the number of keys in `evaluated_status_counts`
- **AND** the field MUST be `0` when no components were explicitly evaluated

#### Scenario: Status key counts remain advisory only

- **WHEN** a caller inspects subscription long-run governance status
- **THEN** the status key count fields MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior
- **AND** the fields MUST NOT be treated as health, readiness, PID liveness, or process ownership proof

