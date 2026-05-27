## ADDED Requirements

### Requirement: Subscription governance evaluation summary SHALL expose not-evaluated presence

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.has_not_evaluated_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Fully evaluated components report false

- **WHEN** all governance components have been evaluated as stale or fresh
- **THEN** `governance.evaluation_summary.has_not_evaluated_component` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Not-evaluated components report true

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.has_not_evaluated_component` MUST be `true`
- **AND** the field MUST remain consistent with `not_evaluated_count > 0`

#### Scenario: Summary views preserve not-evaluated presence

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.has_not_evaluated_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays
