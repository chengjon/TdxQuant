## ADDED Requirements

### Requirement: Subscription governance evaluation summary SHALL expose all-components evaluated flag

The subscription long-run status summary SHALL include additive read-only `status_summary.governance.evaluation_summary.all_components_evaluated` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: Not-evaluated components report false

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.all_components_evaluated` MUST be `false`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Fully evaluated components report true

- **WHEN** all governance components have been evaluated as stale or fresh
- **THEN** `governance.evaluation_summary.all_components_evaluated` MUST be `true`
- **AND** the field MUST remain consistent with `not_evaluated_count == 0`

#### Scenario: Summary views preserve all-components evaluated flag

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.all_components_evaluated`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays
