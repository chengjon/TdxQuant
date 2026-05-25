## ADDED Requirements

### Requirement: Subscription governance evaluation summary SHALL expose primary not-evaluated component

The subscription long-run status summary SHALL include additive `status_summary.governance.evaluation_summary.primary_not_evaluated_component` derived from existing evaluation output, without changing reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior.

#### Scenario: No not-evaluated components have null primary not-evaluated component

- **WHEN** all governance components are explicitly evaluated
- **THEN** `governance.evaluation_summary.primary_not_evaluated_component` MUST be `null`
- **AND** the status summary MUST remain advisory and read-only

#### Scenario: Not-evaluated components expose first not-evaluated component

- **WHEN** one or more governance components are not evaluated
- **THEN** `governance.evaluation_summary.primary_not_evaluated_component` MUST equal the first entry in `not_evaluated_components`
- **AND** the field MUST NOT trigger reconnect, backoff, restart, lifecycle, HTTP, SSE, or event-stream behavior

#### Scenario: Summary views preserve primary not-evaluated component

- **WHEN** a caller requests bridge watch-status with `--view summary` or `view=summary`
- **THEN** the compact summary payload MUST preserve `governance.evaluation_summary.primary_not_evaluated_component`
- **AND** the summary view MUST NOT expose raw governance reasons/actions arrays

